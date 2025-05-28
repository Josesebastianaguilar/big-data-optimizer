from bson.objectid import ObjectId
from app.models.process import Process, ProcessingStatus, ProcessName, Trigger
from typing import List, Any
from app.database import db
from app.utils.monitor_resources_utils import monitor_resources, get_metrics, dequeue_measurements, get_process_times
from queue import Queue
from threading import Lock
from collections import defaultdict
from datetime import datetime
from app.utils import non_optimized_processing_utils as non_opt_utils
from  app.utils import optimized_processing_utils as opt_utils
from app.utils.general_utils import group_results_to_objects, convert_numpy_types
import pandas as pd
import multiprocessing as mp
import time
import threading
import asyncio
import logging

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
    raise ValueError("Filter process not found")
  filter_metrics = Queue()
  filter_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.025, stop_event, filter_metrics, filter_lock))
  monitor_thread.start()
  try:
    if filter_process_item["optimized"] is True:
      filter_results = await utils.filter_data(df, filter_process_item["parameters"], num_processes)
    else:
      filter_results = utils.filter_data(df, filter_process_item["parameters"], num_processes)
    stop_event.set()
    monitor_thread.join()
    filter_metrics_list = dequeue_measurements(filter_metrics, filter_lock)
    filter_time_metrics = get_process_times(filter_metrics_list)
    normalized_filter_results = filter_results["_id"].tolist()
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
  group_process_item = next((p for p in processes if p["task_process"] == "group"), None)
  if not group_process_item:
    raise ValueError("Group process not found")
  group_metrics = Queue()
  group_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.025, stop_event, group_metrics, group_lock))
  monitor_thread.start()
  try:
    group_results = utils.group_data(df, group_process_item["parameters"])
    stop_event.set()
    monitor_thread.join()
    group_metrics_list = dequeue_measurements(group_metrics, group_lock)
    group_time_metrics = get_process_times(group_metrics_list)
    normalized_group_results = utils.map_groupped_records(group_results, "_id")
    grouped_objects = group_results_to_objects(normalized_group_results)
    if group_process_item["optimized"] is True:
      grouped_objects = convert_numpy_types(grouped_objects)
    output_group_data_size = len(grouped_objects) + sum(len(obj["values"]) for obj in grouped_objects)
    
    await store_success(group_process_item["_id"], input_group_data_size, output_group_data_size, group_metrics_list, group_time_metrics, grouped_objects)
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    group_metrics_list = dequeue_measurements(group_metrics, group_lock)
    group_time_metrics = get_process_times(group_metrics_list)
    await store_errors(group_process_item["_id"], input_group_data_size, group_metrics_list, group_time_metrics, e)
  finally:
    stop_event.set()
    monitor_thread.join()

async def apply_aggregation(df: pd.DataFrame, processes: List[dict], utils):
  input_aggregation_data_size = len(df)
  aggregation_process_item = next((p for p in processes if p["task_process"] == "aggregation"), None)
  if not aggregation_process_item:
    raise ValueError("Aggregation process not found")
  aggregation_metrics = Queue()
  aggregation_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.025, stop_event, aggregation_metrics, aggregation_lock))
  monitor_thread.start()
  try:
    aggregation_results = utils.aggregate_data(df, aggregation_process_item["parameters"])
    stop_event.set()
    monitor_thread.join()
    aggregation_metrics_list = dequeue_measurements(aggregation_metrics, aggregation_lock)
    aggregation_time_metrics = get_process_times(aggregation_metrics_list)
    if aggregation_process_item["optimized"] is True:
      aggregation_results = convert_numpy_types(aggregation_results)
    await store_success(aggregation_process_item["_id"], input_aggregation_data_size, None, aggregation_metrics_list, aggregation_time_metrics, aggregation_results)
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    aggregation_metrics_list = dequeue_measurements(aggregation_metrics, aggregation_lock)
    aggregation_time_metrics = get_process_times(aggregation_metrics_list)
    await store_errors(aggregation_process_item["_id"], input_aggregation_data_size, aggregation_metrics_list, aggregation_time_metrics, e)
  

async def process_data(df: pd.DataFrame, processes: List[Process], utils, num_processes, actions: List[ProcessName], optimized):
  if "filter" in actions:
    try:
      filter_results = await apply_filter(df, processes, utils, num_processes)
      if "group" in actions and "aggregation" in actions:
        await apply_groupping(filter_results, processes, utils, optimized)
        await apply_aggregation(filter_results, processes, utils)
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
    await apply_groupping(df, processes, utils, optimized)
    await  apply_aggregation(df, processes, utils)
  elif "group" in actions:
    await apply_groupping(df, processes, utils, optimized)
  elif "aggregation" in actions:
    await apply_aggregation(df, processes, utils)

async def start_cron_initiated_process(process_id: str, repository_id: str, actions: List[Any], iteration: int = 1):
  """
  Start a cron initiated process for a given repository and process_id.
  """
  records = []
  total_records = await db["records"].count_documents({"repository": ObjectId(repository_id)})
  processes = await db["processes"].find({"process_id": process_id, "trigger_type": "system", "iteration": iteration, "status": "in_progress"}).to_list(length=None)
  optimized_processes = [process for process in processes if process["optimized"] is True]
  non_optimized_processes = [process for process in processes if process["optimized"] is False]
  batch_size = 10000
  for i in range(0, total_records, batch_size):
    batch = await db["records"].find({"repository": ObjectId(repository_id)}).skip(i).limit(batch_size).to_list(length=None)
    records.extend(batch)
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
      logging.info("Starting cron initiated process.")
      existing_executing_processes = await db["processes"].find({"status": "in_progress"}, {"results": 0, "metrics": 0, "errors": 0}).to_list(length=None)
        
      if len(existing_executing_processes) > 0:
          logging.info(f"There are executing processes. The system will try again at the next cron interval.")
          return
      repositories = await db["repositories"].find({"data_ready": True}).to_list(length=None)
      if len(repositories) == 0:
        logging.info("No repositories found with data ready. Skipping cron initiated process.")
        return
      
      for repository in repositories:
        processes = await db["processes"].find({"repository": repository["_id"], "iteration": 1, "repository_version": repository["version"], "trigger_type": "user"}, {"results": 0, "metrics": 0}).to_list(length=None)
        
        if len(processes) == 0:
          logging.info(f"Repository {repository['_id']} has no user initiated processes. Skipping.")
          continue
        
        grouped_processes = defaultdict(list)
        for user_initiated_process in processes:
            grouped_processes[user_initiated_process["process_id"]].append(user_initiated_process)
        
        valid_process_ids = []
        for process_id, process_group in grouped_processes.items():
          existing_cron_processes = await db["processes"].find({"repository": repository["_id"], "process_id": process_id, "trigger_type": "system"}).to_list(length=None)
          if len(existing_cron_processes) == 0:
            valid_process_ids.append(str(process_id))
        
        for i in range(10):
          for process_id, process_group in grouped_processes.items():
            if str(process_id) not in valid_process_ids:
              logging.info(f"Process {process_id} already has cron initiated processes for repository {repository['_id']}. Skipping.")
              continue
            cron_processes = []
            all_actions = []
            for process in process_group:
              if all_actions == []:
                all_actions = process["actions"]
              cron_processes.append({
                "parameters": process["parameters"],
                "actions": process["actions"],
                "task_process": process["task_process"],
                "status": "in_progress",
                "repository": repository["_id"],
                "process_id": process_id,
                "trigger_type": "system",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "optimized": process["optimized"],
                "iteration": i + 1,
                "validated": False
              })
            await db["processes"].insert_many(cron_processes)
            logging.info(f"Inserted {len(cron_processes)} cron processes for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}. Starting processing.")
            try:
              await start_cron_initiated_process(process_id, repository["_id"], all_actions, i + 1)
              logging.info(f"Started cron initiated process for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}.")
            except Exception as e:
              logging.error(f"Error in cron initiated process: {e} for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}")
              continue
      logging.info("Cron initiated processes completed successfully.")      
    except Exception as e:
      logging.error(f"Error in cron initiated process: {e}")
      return
