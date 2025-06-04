from bson.objectid import ObjectId
from typing import List, Any
from app.database import db
from app.utils.monitor_resources_utils import monitor_resources, get_metrics, dequeue_measurements, get_process_times, compute_cgroup_cpu_percent
from queue import Queue
from threading import Lock
from app.utils.general_utils import group_results_to_objects, convert_numpy_types
from datetime import datetime
from dotenv import load_dotenv
from app.utils import non_optimized_processing_utils as non_opt_utils
from app.utils import optimized_processing_utils as opt_utils
from app.utils.records_utils import delete_collection_in_batches
from collections import defaultdict
import multiprocessing as mp
import pandas as pd
import threading
import asyncio
import logging
import os

load_dotenv()
PROCESSES_RECORDS_BATCH_SIZE = int(os.getenv("PROCESSES_RECORDS_BATCH_SIZE", "15000"))
PROCESS_RESULTS_BATCH_SIZE = int(os.getenv("PROCESS_RESULTS_BATCH_SIZE", "500"))
USES_CGROUP_CPU_MEASUREMENT = bool(os.getenv("USES_CGROUP_CPU_MEASUREMENT", "").lower() == "true")


async def store_success(process_id, input_data_size, output_data_size, metrics, time_metrics):
  await db["processes"].update_one(
    {"_id": ObjectId(process_id)},
    {"$set": 
      {
        "input_data_size": input_data_size,
        "output_data_size": output_data_size,
        "metrics": metrics,
        **time_metrics,
        "status": "completed",
        "errors": None,
        "updated_at": datetime.now()
      }
    })

async def store_batch(process_item_id, process_id, input_data_size, output_data_size, metrics, batch_number, task_process, trigger_type, iteration, optimized, repository):
  await db["process_results"].insert_one(
    {
      "process_item_id": ObjectId(process_item_id),
      "process_id": ObjectId(process_id),
      "repository": ObjectId(repository),
      "input_data_size": input_data_size,
      "output_data_size": output_data_size,
      "optimized": optimized,
      "batch_number": batch_number,
      "type": task_process,
      "trigger_type": trigger_type,
      "iteration": iteration,
      "metrics": metrics,
      "created_at": datetime.now(),
      "updated_at": datetime.now()
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
        "updated_at": datetime.now()
      }
    })

async def apply_filter(df: pd.DataFrame, processes, utils, num_processes: int, batch_number: int, trigger_type: str, iteration: int):
  input_filter_data_size = len(df)
  filter_process_item = next((p for p in processes if p["task_process"] == "filter"), None)
  if not filter_process_item:
    logging.error("Filter process not found")
    raise ValueError("Filter process not found")
  filter_metrics = Queue()
  filter_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.250, stop_event, filter_metrics, filter_lock))
  monitor_thread.start()
  
  try:
    filter_results = None
    filter_results = utils.filter_data(df, filter_process_item["parameters"])
    stop_event.set()
    monitor_thread.join()
    filter_metrics_list = dequeue_measurements(filter_metrics, filter_lock)
    
    #normalized_filter_results = filter_results["_id"].tolist()
    output_filter_data_size = len(filter_results)
    
    await store_batch(filter_process_item["_id"], filter_process_item["process_id"], input_filter_data_size, output_filter_data_size, filter_metrics_list, batch_number, "filter", trigger_type, iteration, filter_process_item["optimized"], filter_process_item["repository"])

    return filter_results
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    filter_metrics_list = dequeue_measurements(filter_metrics, filter_lock)
    #filter_time_metrics = get_process_times(filter_metrics_list)
    #await store_errors(filter_process["_id"], input_filter_data_size, filter_metrics_list, filter_time_metrics, e)
    logging.error(f"Error in filter process {str(filter_process_item['_id'])}: {e}. skipping filter process batch {batch_number}.")
    
    return 

async def apply_groupping(df: pd.DataFrame, processes, utils, batch_number: int, trigger_type: str, iteration: int):
  input_group_data_size = len(df)
  group_process_item = next((p for p in processes if p["task_process"] == "group"), None)
  if not group_process_item:
    logging.error("Group process not found")
    raise ValueError("Group process not found")
  if group_process_item["optimized"] is not True:
    df = df.to_dict(orient="records")
  group_metrics = Queue()
  group_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.250, stop_event, group_metrics, group_lock))
  monitor_thread.start()
  try:
    group_results = utils.group_data(df, group_process_item["parameters"])
    stop_event.set()
    monitor_thread.join()
    group_metrics_list = dequeue_measurements(group_metrics, group_lock)
    # normalized_group_results = utils.map_groupped_records(group_results, "_id")
    # grouped_objects = group_results_to_objects(normalized_group_results)
    
    # if group_process_item["optimized"] is True:
    #   grouped_objects = convert_numpy_types(grouped_objects)
    
    #output_group_data_size = len(grouped_objects) + sum(len(obj["values"]) for obj in grouped_objects)
    
    await store_batch(group_process_item["_id"], group_process_item["process_id"], input_group_data_size, None, group_metrics_list, batch_number, "group", trigger_type, iteration, group_process_item["optimized"], group_process_item["repository"])
    
    #await store_success(group_process_item["_id"], input_group_data_size, output_group_data_size, group_metrics_list, group_time_metrics, grouped_objects)
    
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    group_metrics_list = dequeue_measurements(group_metrics, group_lock)
    #group_time_metrics = get_process_times(group_metrics_list)
    
    #await store_errors(group_process_item["_id"], input_group_data_size, group_metrics_list, group_time_metrics, e)
    
    logging.error(f"Error in group process {str(group_process_item['_id'])}: {e}. skipping group process batch {batch_number}.")

async def apply_aggregation(df: pd.DataFrame, processes, utils, batch_number: int, trigger_type: str, iteration: int):
  input_aggregation_data_size = len(df)
  aggregation_process_item = next((p for p in processes if p["task_process"] == "aggregation"), None)
  if not aggregation_process_item:
    logging.error("Aggregation process not found")
    raise ValueError("Aggregation process not found")
  aggregation_metrics = Queue()
  aggregation_lock = Lock()
  stop_event = threading.Event()
  monitor_thread = threading.Thread(target=monitor_resources, args=(0.250, stop_event, aggregation_metrics, aggregation_lock))
  monitor_thread.start()
  try:
    aggregation_results = utils.aggregate_data(df, aggregation_process_item["parameters"])
    stop_event.set()
    monitor_thread.join()
    aggregation_metrics_list = dequeue_measurements(aggregation_metrics, aggregation_lock)
    
    # if aggregation_process_item["optimized"] is True:
    #   aggregation_results = convert_numpy_types(aggregation_results)
    
    await store_batch(aggregation_process_item["_id"], aggregation_process_item["process_id"], input_aggregation_data_size, None, aggregation_metrics_list, batch_number, "aggregation", trigger_type, iteration, aggregation_process_item["optimized"], aggregation_process_item["repository"])
    #await store_success(aggregation_process_item["_id"], input_aggregation_data_size, None, aggregation_metrics_list, aggregation_time_metrics, aggregation_results)
    
  except Exception as e:
    stop_event.set()
    monitor_thread.join()
    aggregation_metrics_list = dequeue_measurements(aggregation_metrics, aggregation_lock)
    #aggregation_time_metrics = get_process_times(aggregation_metrics_list)
    
    #await store_errors(aggregation_process_item["_id"], input_aggregation_data_size, aggregation_metrics_list, aggregation_time_metrics, e)
    logging.error(f"Error in aggregation process {str(aggregation_process_item['_id'])}: {e}. skipping aggregation process batch {batch_number}.")
    return
  

async def process_data(df: pd.DataFrame, processes, utils, num_processes, actions, optimized, batch_number: int, trigger_type, iteration):
  if "filter" in actions:
    try:
      filter_results = await apply_filter(df, processes, utils, num_processes, batch_number, trigger_type, iteration)
      if "group" in actions and "aggregation" in actions:
        await apply_groupping(filter_results, processes, utils, batch_number, trigger_type, iteration),
        await apply_aggregation(filter_results, processes, utils, batch_number, trigger_type, iteration)
      elif "group" in actions:
        await apply_groupping(filter_results, processes, utils, batch_number, trigger_type, iteration)
      elif "aggregation" in actions:
        await apply_aggregation(filter_results, processes, utils, batch_number, trigger_type, iteration)
    except Exception as e:
      if "group" in actions:
        group_process = next((p for p in processes if p["task_process"] == "group"), None)
        if group_process:
          await db["processes"].update_one({"_id": group_process_item["_id"]}, {"$set": {"status": "failed", "errors": f"FILTER errors: {str(e)}", "updated_at": datetime.now()}})
      if "aggregation" in actions:
        aggregation_process = next((p for p in processes if p["task_process"] == "aggregation"), None)
        if aggregation_process:
          await db["processes"].update_one({"_id": aggregation_process["_id"]}, {"$set": {"status": "failed", "errors": f"FILTER errors: {str(e)}", "updated_at": datetime.now()}})
  elif "group" in actions and "aggregation" in actions:
    await apply_groupping(df, processes, utils, batch_number, trigger_type, iteration),
    await apply_aggregation(df, processes, utils, batch_number, trigger_type, iteration)
  elif "group" in actions:
    await apply_groupping(df, processes, utils, batch_number, trigger_type, iteration)
  elif "aggregation" in actions:
    await apply_aggregation(df, processes, utils, batch_number, trigger_type, iteration)
    
async def start_metrics_results_gathering(process_id: str, processes: List[Any], repository: Any, actions, trigger_type: str, total_batches, total_num_processes: int = 1):
  """
  Gather metrics and results for a given process.
  """
  logging.info(f"Starting results gathering for process_id {process_id}")
  for process in processes:
    current_process = await db["processes"].find_one({"_id": ObjectId(process["_id"]), "status": "in_progress"})
    if current_process:
      process_input_data_size = 0
      process_output_data_size = 0
      process_time_metrics = {}
      process_metrics = []
      
      if current_process["task_process"] == "filter" or "filter" not in actions:
        process_input_data_size = repository["current_data_size"]
      
      if current_process["task_process"] != "filter" and "filter" in actions:
        input_filter_data_size_list = await db["process_results"].aggregate([
          {"$match": {"type": "filter", "trigger_type": trigger_type, "iteration": current_process["iteration"], "optimized": current_process["optimized"], "process_id": ObjectId(current_process["process_id"]) }},
          {"$group": {"_id": None, "output_data_size": {"$sum": "$output_data_size"}}}
        ]).to_list(length=None)
        
        process_input_data_size = input_filter_data_size_list[0]["output_data_size"] if input_filter_data_size_list else 0
        
      for i in range(0, total_batches, PROCESS_RESULTS_BATCH_SIZE):
        batch_results = await db["process_results"].find({"process_item_id": ObjectId(process["_id"])}, {"metrics": 1, "results": 1, "output_data_size": 1}).sort("batch_number", 1).skip(i).limit(PROCESS_RESULTS_BATCH_SIZE).to_list(length=None)
        process_metrics.extend([item for result in batch_results if result["metrics"] is not None for item in result["metrics"]])
        if current_process["task_process"] != "aggregation":
          process_output_data_size += sum(result["output_data_size"] for result in batch_results if result["output_data_size"] is not None)
          
          
      process_metrics.sort(key=lambda x: x["timestamp"] if isinstance(x, dict) and "timestamp" in x else 0)
      
      if USES_CGROUP_CPU_MEASUREMENT is True:
        process_metrics = compute_cgroup_cpu_percent(process_metrics, total_num_processes)
      
      first_process_metric = process_metrics[0] if len(process_metrics) > 0 else None
      last_process_metric = process_metrics[::-1][0]  if len(process_metrics) > 0 else None
      
      if first_process_metric != None and last_process_metric != None:
        process_time_metrics = get_process_times([first_process_metric, last_process_metric])
        
      if len(process_metrics) == 0:
        process_time_metrics = {"duration": 0}
      
      if current_process["task_process"] == "aggregation":
        process_output_data_size = None
      
      await store_success(process["_id"], process_input_data_size, process_output_data_size, process_metrics, process_time_metrics)
      logging.info(f"Process {process['_id']} completed successfully")
    else:
      logging.warning(f"Process {process['_id']} is not in progress, skipping results gathering")
  logging.info(f"All processes for process_id {process_id} completed successfully")
  
async def start_process(process_id: str, repository_id: str, actions, iteration: int = 1, trigger_type: str = "user"):
    """
    Process data for a given collection and queries.
    """
    # Fetch data from the database
    try:
      repository = await db["repositories"].find_one({"_id": ObjectId(repository_id)}, {"current_data_size": 1})
      total_records = repository["current_data_size"]
      logging.info(f"Total records to process: {total_records} for repository {repository_id}")
      total_batches = total_records // PROCESSES_RECORDS_BATCH_SIZE + (1 if total_records % PROCESSES_RECORDS_BATCH_SIZE > 0 else 0)
      logging.info(f"Batch size: {PROCESSES_RECORDS_BATCH_SIZE}")
      logging.info(f"Total batches per process: {total_batches}")
      processes = await db["processes"].find({"process_id": ObjectId(process_id), "repository": ObjectId(repository_id), "trigger_type": trigger_type, "iteration": iteration, "status": "in_progress"}).to_list(length=None)
      optimized_processes = [process for process in processes if process["optimized"] is True]
      non_optimized_processes = [process for process in processes if process["optimized"] is False]
      total_num_processes = mp.cpu_count()
      
      for j in range(0, 2, 1):
        for i in range(0, total_records, PROCESSES_RECORDS_BATCH_SIZE):
          batch_number = (i // PROCESSES_RECORDS_BATCH_SIZE) + 1
          batch = await db["records"].find({"repository": ObjectId(repository_id)}).sort("_id", 1).skip(i).limit(PROCESSES_RECORDS_BATCH_SIZE).to_list(length=None)
          df = pd.DataFrame([{"_id": record["_id"], **record["data"]} for record in batch])
          
          if j == 0:
            await process_data(df, optimized_processes, opt_utils, max(total_num_processes - 3, 1), actions, True, batch_number, trigger_type, iteration)
          elif j == 1:
            await process_data(df, non_optimized_processes, non_opt_utils, None, actions, False, batch_number, trigger_type, iteration),
      
      await start_metrics_results_gathering(process_id, processes, repository, actions, trigger_type, total_batches, total_num_processes)
    except Exception as e:
      logging.error(f"Error processing data for process_id {process_id}: {e}")
      raise e

async def prepare_cron_initiated_processes():
    """
    Process data for a given collection and queries.
    """
    try:
      logging.info("Starting cron initiated process.")
      # existing_executing_processes = await db["processes"].find({"status": "in_progress"}, {"results": 0, "metrics": 0, "errors": 0}).to_list(length=None)
        
      # if len(existing_executing_processes) > 0:
      #     logging.info(f"There are executing processes. The system will try again at the next cron interval.")
      #     return
      repositories = await db["repositories"].find({"data_ready": True}).to_list(length=None)
      if len(repositories) == 0:
        logging.info("No repositories found with data ready. Skipping cron initiated process.")
        return
      
      for repository in repositories:
        processes = await db["processes"].find({"repository": repository["_id"], "iteration": 1, "repository_version": repository["version"], "trigger_type": "user"}, {"metrics": 0}).to_list(length=None)
        
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
          logging.info(f"Iteration {i + 1} for repository {repository['_id']}")
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
              await start_process(str(process_id), str(repository["_id"]), all_actions, i + 1, "system")
              logging.info(f"Started cron initiated process for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}.")
            except Exception as e:
              logging.error(f"Error in cron initiated process: {e} for repository {repository['_id']} and process_id {process_id} at iteration {i + 1}")
              continue
      logging.info("Cron initiated processes completed successfully.")      
    except Exception as e:
      logging.error(f"Error in cron initiated process: {e}")
      return
    

async def reset_processes(repository_id: str):
    """
    Reset all processes for a given repository.
    """
    try:
      processes_query = {"repository": ObjectId(repository_id)}
      processes = await db["processes"].find(processes_query, {"_id": 1}).to_list(length=None)
      
      processes_ids = [ObjectId(process["_id"]) for process in processes]
      processes_results_query = {"process_item_id": {"$in": processes_ids}}
      
      logging.info(f"Resetting processes for repository {repository_id}")
      await delete_collection_in_batches(db["processes"], processes_query)
      logging.info(f"Deleted {len(processes)} processes for repository {repository_id}")
      logging.info(f"Deleting process results for repository {repository_id}")
      await delete_collection_in_batches(db["process_results"], processes_results_query)
      logging.info(f"Deleted process results for repository {repository_id}")
      
      logging.info(f"Processes for repository {repository_id} reset successfully.")
    except Exception as e:
      logging.error(f"Error resetting processes for repository {repository_id}: {e}")
      raise e        

