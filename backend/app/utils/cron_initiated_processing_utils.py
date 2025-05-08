from bson.objectid import ObjectId
from app.models.process import Process, ProcessingStatus, ProcessName, Trigger
from typing import List
from app.database import db
from app.utils.monitor_resources_utils import monitor_resources, get_metrics, dequeue_measurements, get_process_times
from queue import Queue
from threading import Lock
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime
import utils.non_optimized_processing_utils as non_opt_utils
import utils.optimized_processing_utils as opt_utils
import pandas as pd
import multiprocessing as mp
import time
import threading
import asyncio
import logging
import os

load_dotenv()
logging.basicConfig(filename=os.getenv("ERROR_LOG_PATH", "error.log"), level=logging.ERROR)

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
        "status": ProcessingStatus.COMPLETED,
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
        "status": ProcessingStatus.FAILED,
        "errors": str(errors),
        "updated_at": time_metrics["end_time"]
      }
    })

async def apply_filter(df: pd.DataFrame, processes: List[dict], utils, num_processes: int):
  input_filter_data_size = len(df)
  filter_process_item = next((p for p in processes if p["task_process"] == ProcessName.FILTER), None)
  if not filter_process_item:
    raise ValueError("Filter process not found")
  filter_metrics = Queue()
  filter_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.5, stop_event, filter_metrics, filter_lock))
  monitor_thread.start()
  filters_metrics_process = psutil.Process()
  try:
    filter_results = await utils.filter_data(df, filter_process_item["parameters"], num_processes)
    stop_event.set()
    monitor_thread.join()
    filter_metrics_list = dequeue_measurements(filter_metrics, filter_lock)
    filter_time_metrics = get_process_times(filter_metrics_list)
    normalized_filter_results = filter_results["_id"].to_dict(orient="records").apply(lambda x: str(x))
    output_filter_data_size = len(normalized_filter_results)

    await store_success(filter_process_item["_id"], input_filter_data_size, output_filter_data_size, filter_metrics_list, filter_time_metrics, normalized_filter_results)

    return filter_results
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    filter_metrics_list = dequeue_measurements(filter_metrics, filter_lock)
    filter_time_metrics = get_process_times(filter_metrics_list)
    await store_errors(filter_process["_id"], input_filter_data_size, filter_metrics_list, filter_time_metrics, e)
    
    raise e
  finally:
    stop_event.set()
    monitor_thread.join()

async def apply_groupping(df: pd.DataFrame, processes: List[dict], utils, optimized):
  if optimized is not True:
    df = df.to_dict(orient="records")
  input_group_data_size = len(df)
  group_process_item = next((p for p in processes if p["task_process"] == ProcessName.GROUP), None)
  if not group_process_item:
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
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    group_metrics_list = dequeue_measurements(group_metrics, group_lock)
    group_time_metrics = get_process_times(group_metrics_list)
    await store_errors(group_process["_id"], input_group_data_size, group_metrics_list, group_time_metrics, e)
  finally:
    stop_event.set()
    monitor_thread.join()

async def apply_aggregation(df: pd.DataFrame, processes: List[dict], utils):
  input_aggregation_data_size = len(df)
  aggregation_process_item = next((p for p in processes if p["task_process"] == ProcessName.AGGREGATION), None)
  if not aggregation_process_item:
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
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    aggregation_metrics_list = dequeue_measurements(aggregation_metrics, aggregation_lock)
    aggregation_time_metrics = get_process_times(aggregation_metrics_list)
    await store_errors(aggregation_process_item["_id"], input_aggregation_data_size, aggregation_metrics_list, aggregation_time_metrics, e)
  finally:
    stop_event.set()
    monitor_thread.join()
  

async def process_data(df: pd.DataFrame, processes: List[Process], utils, num_processes, actions: List[ProcessName], optimized):
  if ProcessName.FILTER in actions:
    try:
      filter_results = await apply_filter(df, processes, utils, num_processes)
      if ProcessName.GROUP in actions and ProcessName.AGGREGATION in actions:
        await apply_groupping(filter_results, processes, utils, optimized)
        await apply_aggregation(filter_results, processes, utils)
      elif ProcessName.GROUP in actions:
        await apply_groupping(filter_results, processes, utils, optimized)
      elif ProcessName.AGGREGATION in actions:
        await apply_aggregation(filter_results, processes, utils)
    except Exception as e:
      if ProcessName.GROUP in actions:
        group_process = next((p for p in processes if p["task_process"] == ProcessName.GROUP), None)
        if group_process:
          await db["processes"].update_one({"_id": group_process["_id"]}, {"$set": {"status": ProcessingStatus.FAILED, "errors": f"FILTER errors: {str(e)}", "updated_at": time.perf_counter()}})
      if ProcessName.AGGREGATION in actions:
        aggregation_process = next((p for p in processes if p["task_process"] == ProcessName.AGGREGATION), None)
        if aggregation_process:
          await db["processes"].update_one({"_id": aggregation_process["_id"]}, {"$set": {"status": ProcessingStatus.FAILED, "errors": f"FILTER errors: {str(e)}", "updated_at": time.perf_counter()}})
  elif ProcessName.GROUP in actions and ProcessName.AGGREGATION in actions:
    await apply_groupping(df, processes, utils, optimized)
    await  apply_aggregation(df, processes, utils)
  elif ProcessName.GROUP in actions:
    await apply_groupping(df, processes, utils, optimized)
  elif ProcessName.AGGREGATION in actions:
    await apply_aggregation(df, processes, utils)

async def start_cron_initiated_process(process_id: ObjectId, repository_id: ObjectId, actions: List[ProcessName], iteration: int = 1):
  """
  Start a cron initiated process for a given repository and process_id.
  """
  records = await db["records"].find({"repository": repository_id}).to_list(length=None)
  processes = await db["processes"].find({"process_id": process_id, "trigger_type": Trigger.CRON, "iteration": iteration, "status": ProcessingStatus.PENDING}).to_list(length=None)
  optimized_processes = [process for process in processes if process["optimized"] is True]
  non_optimized_processes = [process for process in processes if process["optimized"] is False]
  df = pd.DataFrame([{"_id": record["_id"], **record["data"]} for record in records])
  total_num_processes = mp.cpu_count()
  try:
    await process_data(df, non_optimized_processes, non_opt_utils, None, actions, False)
    await process_data(df, optimized_processes, opt_utils, max(total_num_processes - 1, 1), actions, True)
  except Exception as e:
    logging.error(f"Error in cron initiated process: {e} for repository {repository_id} and process_id {process_id} at iteration {iteration}")
  
  
async def prepare_cron_initiated_processes():
    """
    Process data for a given collection and queries.
    """
    try:
      repositories = await db["repositories"].find({"data_ready": True}).to_list(length=None)
      if len(repositories) == 0:
        logging.info("No repositories found with data ready. Skipping cron initiated process.")
        return
      
      for repository in repositories:
        processes = await db["processes"].find({"repository": repository["_id"], "iteration": 1, "repository_version": repository["version"]}, {"results": 0, "metrics": 0}).to_list(length=None)
        
        if len(processes) == 0:
          logging.info(f"Repository {repository['_id']} has no completed processes. Skipping.")
          continue
        cron_processes = [process for process in processes if process["trigger_type"] is Trigger.CRON]
        
        if len(cron_processes) != 0:
          logging.info(f"Repository {repository['_id']} has already cron processes. skipping.")
          continue
        
        user_initiated_processes = [process for process in processes if process["trigger_type"] is Trigger.USER and process["status"] is not ProcessingStatus.PENDING]
        
        if len(user_initiated_processes) == 0:
          logging.info(f"Repository {repository['_id']} has no user initiated processes. skipping.")
          continue
        
        grouped_processes = defaultdict(list)
        for user_initiated_process in user_initiated_processes:
            grouped_processes[user_initiated_process["process_id"]].append(user_initiated_process)
        
        for i in range(10):
          for process_id, process_group in grouped_processes.items():
            cron_processes = []
            all_actions = []
            for process in process_group:
              if all_actions == []:
                all_actions = process["actions"]
              cron_processes.append({
                "parameters": process["parameters"],
                "actions": process["actions"],
                "task_process": process["task_process"],
                "status": ProcessingStatus.PENDING,
                "repository": repository["_id"],
                "process_id": process_id,
                "trigger_type": Trigger.CRON,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "optimized": process["optimized"],
                "iteration": i + 1,
                "validated": False
              })
            await db["processes"].insert_many(cron_processes)
            logging.info(f"Inserted {len(cron_processes)} cron processes for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}. Starting processing.")
            try:
              await start_cron_initiated_process(process_id, repository["_id"], all_actions["all_processes"], i + 1)
              logging.info(f"Started cron initiated process for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}.")
            except Exception as e:
              logging.error(f"Error in cron initiated process: {e} for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}")
              continue
    except Exception as e:
      logging.error(f"Error in cron initiated process: {e}")
      return
