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
from  app.utils import non_optimized_processing_utils as non_opt_utils
from  app.utils import optimized_processing_utils as opt_utils
import pandas as pd
import multiprocessing as mp
import time
import threading
import asyncio
import logging
import os

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

def validate_group_processes(processes: List[dict]):
  """
  Validate group processes.
  """
  if len(processes) == 0 or "results" not in processes[0]:
    logging.error("Invalid process data: 'results' field is missing.")
    return {"valid": [], "invalid": []}
  valid = []
  invalid = []
  base_results = processes[0]["results"] if len(processes) != 0 else {}
  for key in base_results.keys():
    base_values = [str(value) for value in base_results[key] if value is not None]  
    for process in processes:
      if key not in process["results"]:
        invalid.append(str(process["_id"]))
        continue
      for value in process["results"][key]:
        if value is None:
          invalid.append(str(process["_id"]))
          continue
        if str(value) not in base_values:
          invalid.append(str(process["_id"]))
          break
    
  invalid = list(set(invalid))
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
  base_results = processes[0]["results"] if len(processes) != 0 else {}
  for key in base_results.keys():
    for process in processes:
      if key not in process["results"]:
        invalid.append(str(process["_id"]))
        continue
      if process["results"][key] != base_results[key]:
        invalid.append(str(process["_id"]))
        continue
    
  invalid = list(set(invalid))
  valid = [process["_id"] for process in processes if str(process["_id"]) not in invalid]
  return {"valid": valid, "invalid": invalid}

async def validate_complete_processes(trigger_type: Trigger):
  try:
    processes = await db["processes"].find({"trigger_type": trigger_type, "status": ProcessingStatus.COMPLETED, "validated": False}).to_list(length=None)
    if len(processes) == 0:
      logging.info(f"No completed processes non validated found for trigger type: {trigger_type}")
      return
    
    grouped_processes = defaultdict(list)
    for process in processes:
      grouped_processes[process["process_id"]].append(process)
    
    filter_validation = {"valid": [], "invalid": []}
    group_validation = {"valid": [], "invalid": []}
    aggregation_validation = {"valid": [], "invalid": []}
    for process_id, process_group in grouped_processes.items():
      if len(process_group) != 0:
        repository_version = process_group[0]["repository_version"]
        actions = process_group[0]["actions"]
        
        if ProcessName.filter in actions:
          filter_processes = [p for p in process_group if p["task_process"] == ProcessName.filter]
          filter_validation = validate_filter_processes(filter_processes)
          logging.info(f"Validated filter processes for process_id: {process_id} for task_process: {ProcessName.filter}")
        if ProcessName.group in actions:
          group_processes = [p for p in process_group if p["task_process"] == ProcessName.group]
          group_validation = validate_group_processes(group_processes)
          logging.info(f"Validated group processes for process_id: {process_id} for task_process: {ProcessName.group}")
        if ProcessName.aggregation in actions:
          aggregation_processes = [p for p in process_group if p["task_process"] == ProcessName.aggregation]
          aggregation_validation = validate_aggregation_processes(aggregation_processes)
          logging.info(f"Validated aggregation processes for process_id: {process_id} for task_process: {ProcessName.aggregation}")
        
        await db["processes"].update_many({"_id": {"$in": filter_validation.valid + group_validation.valid + aggregation_validation.valid}}, {"$set": {"validated": True, "valid": True}})
        await db["processes"].update_many({"_id": {"$in": filter_validation.invalid + group_validation.invalid + aggregation_validation.invalid}}, {"$set": {"validated": True, "valid": False}})
        logging.info(f"Stored validation results for process_id: {process_id} for trigger_type: {trigger_type}")
        
        return
  except Exception as e:
    logging.error(f"Error in validate_complete_processes: {e}")
    return
    
async def init_validation():
    """
    Process data for a given collection and queries.
    """
    try:
      await validate_complete_processes(Trigger.SYSTEM)
      await validate_complete_processes(Trigger.USER)
    except Exception as e:
      logging.error(f"Error in validation: {e}")
      return
