from bson.objectid import ObjectId
from app.models.process import Process, ProcessingStatus, ProcessName, Trigger
from typing import List
from app.database import db
from app.utils.monitor_resources_utils import monitor_resources, get_metrics, dequeue_measurements, get_process_times
from queue import Queue
from threading import Lock
from collections import defaultdict
from datetime import datetime
from  app.utils import non_optimized_processing_utils as non_opt_utils
from  app.utils import optimized_processing_utils as opt_utils
import pandas as pd
import multiprocessing as mp
import time
import threading
import asyncio
import logging

def validate_filter_processes(processes: List[dict]):
  """
  Validate filter processes.
  """
  if len(processes) == 0 or "results" not in processes[0]:
    logging.error("Invalid process data: 'results' field is missing.")
    return {"valid": [], "invalid": []}
  base_results = set(str(_id) for _id in processes[0]["results"] if _id is not None) if processes else set()
  invalid = {str(process["_id"]) for process in processes for result in process["results"] if result is None or str(result) not in base_results}
  valid = [process["_id"] for process in processes if str(process["_id"]) not in invalid]
  
  return {"valid": valid, "invalid": list(invalid)}

def validate_group_processes(processes):
  """
  Validate group processes with results as a list of {group, values} objects.
  Handles both single and multiple group keys.
  """
  if len(processes) == 0 or "results" not in processes[0]:
      logging.error("Invalid process data: 'results' field is missing.")
      return {"valid": [], "invalid": []}

  valid = []
  invalid = []

  # Helper to normalize group key to a tuple (for consistent comparison)
  def normalize_group_key(group):
      if isinstance(group, list):
          return tuple(group)
      return (group,)

  # Build mapping from group key to set of values for the base process
  def group_to_set(results):
      mapping = {}
      for obj in results:
          group_key = normalize_group_key(obj["group"])
          mapping[group_key] = set(str(v) for v in obj["values"] if v is not None)
      return mapping

  base_results = processes[0]["results"] if processes else []
  base_mapping = group_to_set(base_results)

  for process in processes:
      proc_mapping = group_to_set(process["results"])
      # Compare group keys
      if set(proc_mapping.keys()) != set(base_mapping.keys()):
          invalid.append((process["_id"]))
          continue
      # Compare values for each group
      for group_key in base_mapping:
          if proc_mapping[group_key] != base_mapping[group_key]:
              invalid.append(str(process["_id"]))
              break

  valid = [process["_id"] for process in processes if str(process["_id"]) not in invalid]
  return {"valid": valid, "invalid": invalid}

def validate_aggregation_processes(processes: List[dict]):
  """
  Validate aggregation processes.
  """
  if len(processes) == 0 or "results" not in processes[0]:
    logging.error("Invalid process data: 'results' field is missing.")
    return {"valid": [], "invalid": []}
  valid = []
  invalid = []
  base_results = processes[0]["results"] if len(processes) != 0 else []
  for i, base_result in enumerate(base_results):
    for key in base_result.keys():
      for process in processes:
        # Check if process["results"] has enough items
        if i >= len(process["results"]) or key not in process["results"][i]:
          invalid.append(str(process["_id"]))
          continue
        if key != "property" and abs(process["results"][i][key] - base_result[key]) > 0.002:
          invalid.append(str(process["_id"]))
          continue
    
  valid = [process["_id"] for process in processes if str(process["_id"]) not in invalid]
  return {"valid": valid, "invalid": invalid}

async def validate_complete_processes(trigger_type: Trigger):
  try:
    processes = await db["processes"].find({"trigger_type": trigger_type, "status": "completed", "validated": False}).to_list(length=None)
    if len(processes) == 0:
      logging.info(f"No completed processes non validated found for trigger type: {trigger_type}")
      return
    
    grouped_processes = defaultdict(list)
    for process in processes:
      grouped_processes[process["process_id"]].append(process)
    
    filter_valid = []
    filter_invalid = []
    group_valid = []
    group_invalid = []
    aggregation_valid = []
    aggregation_invalid = []

    for process_id, process_group in grouped_processes.items():
      if len(process_group) != 0:
        actions = process_group[0]["actions"]

        if "filter" in actions:
          filter_processes = [p for p in process_group if p["task_process"] == "filter"]
          result = validate_filter_processes(filter_processes)
          filter_valid += result["valid"]
          filter_invalid += result["invalid"]
          logging.info(f"Validated filter processes for process_id: {process_id} for task_process: filter")
        if "group" in actions:
          group_processes = [p for p in process_group if p["task_process"] == "group"]
          result = validate_group_processes(group_processes)
          group_valid += result["valid"]
          group_invalid += result["invalid"]
          logging.info(f"Validated group processes for process_id: {process_id} for task_process: group")
        if "aggregation" in actions:
          aggregation_processes = [p for p in process_group if p["task_process"] == "aggregation"]
          result = validate_aggregation_processes(aggregation_processes)
          aggregation_valid += result["valid"]
          print('aggregation_valid', aggregation_valid)
          aggregation_invalid += result["invalid"]
          print('aggregation_invalid', aggregation_invalid)
          logging.info(f"Validated aggregation processes for process_id: {process_id} for task_process: aggregation")
          
        total_valid = filter_valid + group_valid + aggregation_valid
        total_invalid = filter_invalid + group_invalid + aggregation_invalid
        
        total_valid = [ObjectId(_id) for _id in total_valid]
        total_invalid = [ObjectId(_id) for _id in total_invalid]
     
        await db["processes"].update_many({"_id": {"$in": total_valid}},{"$set": {"validated": True, "valid": True}})
        await db["processes"].update_many({"_id": {"$in": total_invalid}}, {"$set": {"validated": True, "valid": False}})
        logging.info(f"Stored validation results for process_id: {process_id} for trigger_type: {trigger_type}")
        
  except Exception as e:
    logging.error(f"Error in validate_complete_processes: {e}")
    return
    
async def init_validation():
    """
    Process data for a given collection and queries.
    """
    try:
      logging.info("Starting validation of completed processes for SYSTEM trigger")
      await validate_complete_processes(Trigger.SYSTEM)
      logging.info("Starting validation of completed processes for USER trigger")
      await validate_complete_processes(Trigger.USER)
      
      return
    except Exception as e:
      logging.error(f"Error in validation: {e}")
      return
