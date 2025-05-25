from fastapi import HTTPException, Response
from bson.objectid import ObjectId
from app.models.process import Process
from typing import List, Any
from app.database import db
from app.utils.monitor_resources_utils import monitor_resources, get_metrics, dequeue_measurements, get_process_times
from queue import Queue
from threading import Lock
from app.utils import non_optimized_processing_utils as non_opt_utils
from  app.utils import optimized_processing_utils as opt_utils
from dotenv import load_dotenv
from bson import json_util
import multiprocessing as mp
import pandas as pd
import time
import threading
import asyncio
import logging
import os

load_dotenv()
logging.basicConfig(filename=os.getenv("ERROR_LOG_PATH", "error.log"), level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s")
logging.basicConfig(filename=os.getenv("INFO_LOG_PATH", "info.log"), level=logging.INFO)
logging.basicConfig(filename=os.getenv("WARNING_LOG_PATH", "warning.log"), level=logging.WARNING)

async def store_success(process_id, input_data_size, output_data_size, metrics, time_metrics, results):
  await db["processes"].update_one(
    {"_id": process_id},
    {"$set": 
      {
        "input_data_size": input_data_size,
        "output_data_size": output_data_size,
        "metrics": metrics,
        **time_metrics,
        "results": results,
        "status": "completed",
        "errors": None,
        "updated_at": time_metrics["end_time"]
      }
    })

async def store_errors(process_id,  input_data_size, metrics, time_metrics, errors):
  await db["processes"].update_one(
    {"_id": process_id},
    {"$set": 
      {
        "input_data_size": input_data_size,
        "metrics": metrics,
        **time_metrics,
        "status": "failed",
        "errors": str(errors),
        "updated_at": time_metrics["end_time"]
      }
    })

async def apply_filter(df: pd.DataFrame, processes, utils, num_processes: int):
  input_filter_data_size = len(df)
  filter_process_item = next((p for p in processes if p["task_process"] == "filter"), None)
  if not filter_process_item:
    logging.error("Filter process not found")
    raise ValueError("Filter process not found")
  filter_metrics = Queue()
  filter_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.5, stop_event, filter_metrics, filter_lock))
  monitor_thread.start()
  
  try:
    filter_results = None
    if filter_process_item["optimized"] is True:
      filter_results = await utils.filter_data(df, filter_process_item["parameters"], num_processes)
    else:
      filter_results = utils.filter_data(df, filter_process_item["parameters"], num_processes)
    stop_event.set()
    monitor_thread.join()
    filter_metrics_list = dequeue_measurements(filter_metrics, filter_lock)
    filter_time_metrics = get_process_times(filter_metrics_list)
    normalized_filter_results = filter_results["_id"].to_dict(orient="records").apply(lambda x: str(x))
    output_filter_data_size = len(normalized_filter_results)
    print(f"Filter data completed")

    await store_success(filter_process_item["_id"], input_filter_data_size, output_filter_data_size, filter_metrics_list, filter_time_metrics, normalized_filter_results)

    stop_event.set()
    monitor_thread.join()
    return filter_results
  except Exception as e:
    print(f"Error in filter process: {e}")
    stop_event.set()
    monitor_thread.join()
    filter_metrics_list = dequeue_measurements(filter_metrics, filter_lock)
    filter_time_metrics = get_process_times(filter_metrics_list)
    await store_errors(filter_process["_id"], input_filter_data_size, filter_metrics_list, filter_time_metrics, e)
    logging.error(f"Error in filter process {str(filter_process_item['_id'])}: {e}")
    
    raise e

async def apply_groupping(df: pd.DataFrame, processes, utils, optimized):
  if optimized is not True:
    df = df.to_dict(orient="records")
  input_group_data_size = len(df)
  group_process_item = next((p for p in processes if p["task_process"] == "group"), None)
  if not group_process_item:
    logging.error("Group process not found")
    raise ValueError("Group process not found")
  group_metrics = Queue()
  group_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.5, stop_event, group_metrics, group_lock))
  monitor_thread.start()
  try:
    group_results = utils.group_data(df, group_process["parameters"])
    stop_event.set()
    monitor_thread.join()
    group_metrics_list = dequeue_measurements(group_metrics, group_lock)
    group_time_metrics = get_process_times(group_metrics_list)
    normalized_group_results = utils.map_groupped_records(group_results, "_id")
    output_group_data_size = sum(len(records) for records in normalized_group_results.values())
    
    await store_success(group_process["_id"], input_group_data_size, output_group_data_size, group_metrics_list, group_time_metrics, normalized_group_results)
    stop_event.set()
    monitor_thread.join()
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    group_metrics_list = dequeue_measurements(group_metrics, group_lock)
    group_time_metrics = get_process_times(group_metrics_list)
    
    await store_errors(group_process["_id"], input_group_data_size, group_metrics_list, group_time_metrics, e)
    
    logging.error(f"Error in group process {str(group_process_item['_id'])}: {e}")
    raise e

async def apply_aggregation(df: pd.DataFrame, processes, utils):
  input_aggregation_data_size = len(df)
  aggregation_process_item = next((p for p in processes if p["task_process"] == "aggregation"), None)
  if not aggregation_process_item:
    logging.error("Aggregation process not found")
    raise ValueError("Aggregation process not found")
  aggregation_metrics = Queue()
  aggregation_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.5, stop_event, aggregation_metrics, aggregation_lock))
  monitor_thread.start()
  try:
    aggregation_results = utils.aggregate_data(df, aggregation_process_item["parameters"])
    stop_event.set()
    monitor_thread.join()
    aggregation_metrics_list = dequeue_measurements(aggregation_metrics, aggregation_lock)
    aggregation_time_metrics = get_process_times(aggregation_metrics_list)
    output_aggregation_data_size = len(aggregation_results)
    await store_success(aggregation_process_item["_id"], input_aggregation_data_size, output_aggregation_data_size, aggregation_metrics_list, aggregation_time_metrics, aggregation_results)
    
    stop_event.set()
    monitor_thread.join()
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    aggregation_metrics_list = dequeue_measurements(aggregation_metrics, aggregation_lock)
    aggregation_time_metrics = get_process_times(aggregation_metrics_list)
    
    await store_errors(aggregation_process_item["_id"], input_aggregation_data_size, aggregation_metrics_list, aggregation_time_metrics, e)
    logging.error(f"Error in aggregation process {str(aggregation_process_item['_id'])}: {e}")
    
    raise e
  

async def process_data(df: pd.DataFrame, processes, utils, num_processes, actions, optimized):
  if "filter" in actions:
    try:
      filter_results = await apply_filter(df, processes, utils, num_processes)
      print('filter_results', filter_results)
      if "group" in actions and "aggregation" in actions:
        await asyncio.gather(
            apply_groupping(filter_results, processes, utils, optimized),
            apply_aggregation(filter_results, processes, utils)
        )
      elif "group" in actions:
        await apply_groupping(filter_results, processes, utils, optimized)
      elif "aggregation" in actions:
        await apply_aggregation(filter_results, processes, utils)
    except Exception as e:
      if "group" in actions:
        group_process = next((p for p in processes if p["task_process"] == "group"), None)
        if group_process:
          await db["processes"].update_one({"_id": group_process["_id"]}, {"$set": {"status": "failed", "errors": f"FILTER errors: {str(e)}", "updated_at": time.perf_counter()}})
      if "aggregation" in actions:
        aggregation_process = next((p for p in processes if p["task_process"] == "aggregation"), None)
        if aggregation_process:
          await db["processes"].update_one({"_id": aggregation_process["_id"]}, {"$set": {"status": "failed", "errors": f"FILTER errors: {str(e)}", "updated_at": time.perf_counter()}})
  elif "group" in actions and "aggregation" in actions:
    await asyncio.gather(
        apply_groupping(df, processes, utils, optimized),
        apply_aggregation(df, processes, utils)
    )
  elif "group" in actions:
    await apply_groupping(df, processes, utils, optimized)
  elif "aggregation" in actions:
    await apply_aggregation(df, processes, utils)

async def start_user_initiated_process(process_id: str, repository_id: str, actions, iteration: int = 1):
    """
    Process data for a given collection and queries.
    """
    # Fetch data from the database
    try:
      total_records = await db["records"].count_documents({"repository": ObjectId(repository_id)})
      records = []
      batch_size = 100_000
      for i in range(0, total_records, batch_size):
        batch = await db["records"].find({"repository": ObjectId(repository_id)}).skip(i).limit(batch_size).to_list(length=None)
        records.extend(batch)
          
      processes = await db["processes"].find({"process_id": ObjectId(process_id), "repository": ObjectId(repository_id), "trigger_type": "user", "iteration": iteration, "status": "in_progress"}).to_list(length=None)
      optimized_processes = [process for process in processes if process["optimized"] is True]
      non_optimized_processes = [process for process in processes if process["optimized"] is False]
      df = pd.DataFrame([{"_id": record["_id"], **record["data"]} for record in records])
      total_num_processes = mp.cpu_count()
      await asyncio.gather(
          process_data(df, non_optimized_processes, non_opt_utils, None, actions, False),
          process_data(df, optimized_processes, opt_utils, max(total_num_processes - 3, 1), actions, True)
      )
    except Exception as e:
      logging.error(f"Error processing data: {e}")
      raise e

    