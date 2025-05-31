from bson.objectid import ObjectId
from typing import List
from app.database import db
from collections import defaultdict
import logging

async def validate_filter_processes(processes: List[dict]):
  """
  Validate filter processes.
  """
  if len(processes) == 0:
    logging.error("No filter processes to validate.")
    return {"valid": [], "invalid": []}
  
  last_batch_results = await db["process_results"].find({"process_id": ObjectId(processes[0]["process_id"])}).sort("batch_number", -1).limit(1).to_list(length=None)
  
  if len(last_batch_results) == 0:
    logging.error("No process results found for the given process_id.")
    raise ValueError("No process results found for the given process_id.")
  
  invalid = []
  
  for i in range(last_batch_results[0]["batch_number"]):
    current_batches = await db["process_results"].find({"process_id": ObjectId(processes[0]["process_id"]), "batch_number": i + 1}, {"results": 1}).to_list(length=None)
    base_results = set(str(_id) for _id in current_batches[0]["results"] if _id is not None) if current_batches[0] else set()
    invalid_in_batches = {str(batch["process_item_id"]) for batch in current_batches for result in batch["results"] if result is None or str(result) not in base_results}
    invalid.extend(invalid_in_batches)
  
  valid = [process["_id"] for process in processes if str(process["_id"]) not in invalid]
  
  return {"valid": valid, "invalid": list(invalid)}

async def validate_group_processes(processes):
  """
  Validate group processes with results as a list of {group, values} objects.
  Handles both single and multiple group keys.
  """
  if len(processes) == 0:
      logging.error("No group processes to validate.")
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
    
  last_batch_results = await db["process_results"].find({"process_id": ObjectId(processes[0]["process_id"])}).sort("batch_number", -1).limit(1).to_list(length=None)
  
  if len(last_batch_results) == 0:
      logging.error("No process results found for the given process_id.")
      raise ValueError("No process results found for the given process_id.")
  
  for i in range(last_batch_results[0]["batch_number"]):
      current_batches = await db["process_results"].find({"process_id": ObjectId(processes[0]["process_id"]), "batch_number": i + 1}, {"results": 1}).to_list(length=None)
      if not current_batches:
          continue
      
      base_results = current_batches[0]["results"] if current_batches else []
      base_mapping = group_to_set(base_results)
      
      for batch in current_batches:
          proc_mapping = group_to_set(batch["results"])
          # Compare group keys
          if set(proc_mapping.keys()) != set(base_mapping.keys()):
              invalid.append(str(batch["process_item_id"]))
              continue
          # Compare values for each group
          for group_key in base_mapping:
              if proc_mapping[group_key] != base_mapping[group_key]:
                  invalid.append(str(batch["process_item_id"]))
                  break
  
  invalid = list(set(invalid))
  valid = [process["_id"] for process in processes if str(process["_id"]) not in invalid]
  
  return {"valid": valid, "invalid": invalid}

async def validate_aggregation_processes(processes: List[dict]):
  """
  Validate aggregation processes.
  """
  if len(processes) == 0:
    logging.error("No aggregation processes to validate.")
    return {"valid": [], "invalid": []}
  
  valid = []
  invalid = []
  last_batch_results = await db["process_results"].find({"process_id": ObjectId(processes[0]["process_id"])}).sort("batch_number", -1).limit(1).to_list(length=None)
  
  if len(last_batch_results) == 0:
    logging.error("No process results found for the given process_id.")
    raise ValueError("No process results found for the given process_id.")
  
  for i in range(last_batch_results[0]["batch_number"]):
    current_batches = await db["process_results"].find({"process_id": ObjectId(processes[0]["process_id"]), "batch_number": i + 1}, {"results": 1}).to_list(length=None)
    if not current_batches:
      continue
    
    base_results = current_batches[0]["results"] if current_batches else []
    for current_batch in current_batches:
      batch_results = current_batch["results"]
      
      if len(batch_results) != len(base_results):
        invalid.append(str(current_batch["process_item_id"]))
        continue
      for batch_result in batch_results:
        base_result = next((r for r in base_results if r["property"] == batch_result["property"]), None)
        
        if base_result is None or set(base_result.keys()) != set(batch_result.keys()):
          invalid.append(str(current_batch["process_item_id"]))
          break
        
        for key in base_result.keys():
          not_nones_condition = (batch_result[key] is not None and base_result[key] is None) or (batch_result[key] is None and base_result[key] is not None)
          
          if key != "property" and (not_nones_condition or abs(batch_result[key] - base_result[key]) > 0.002):
            invalid.append(str(current_batch["process_item_id"]))
            break
  
  invalid = list(set(invalid))
  valid = [process["_id"] for process in processes if str(process["_id"]) not in invalid]
  
  return {"valid": valid, "invalid": invalid}

async def init_validation():
  try:
    processes = await db["processes"].find({"status": "completed", "validated": False}).to_list(length=None)
    if len(processes) == 0:
      logging.info("No completed processes to validate or all processes are already validated.")
      return
    
    logging.info(f"Found {len(processes)} processes to validate.")
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
          result = await validate_filter_processes(filter_processes)
          filter_valid += result["valid"]
          filter_invalid += result["invalid"]
          logging.info(f"Validated filter processes for process_id: {process_id} for task_process: filter")
        if "group" in actions:
          group_processes = [p for p in process_group if p["task_process"] == "group"]
          result = await validate_group_processes(group_processes)
          group_valid += result["valid"]
          group_invalid += result["invalid"]
          logging.info(f"Validated group processes for process_id: {process_id} for task_process: group")
        if "aggregation" in actions:
          aggregation_processes = [p for p in process_group if p["task_process"] == "aggregation"]
          result = await validate_aggregation_processes(aggregation_processes)
          aggregation_valid += result["valid"]
          aggregation_invalid += result["invalid"]
          logging.info(f"Validated aggregation processes for process_id: {process_id} for task_process: aggregation")
          
        total_valid = list(set(filter_valid + group_valid + aggregation_valid))
        total_invalid = list(set(filter_invalid + group_invalid + aggregation_invalid))
        
        total_valid = [ObjectId(_id) for _id in total_valid]
        total_invalid = [ObjectId(_id) for _id in total_invalid]
     
        await db["processes"].update_many({"_id": {"$in": total_valid}},{"$set": {"validated": True, "valid": True}})
        await db["processes"].update_many({"_id": {"$in": total_invalid}}, {"$set": {"validated": True, "valid": False}})
        logging.info(f"Stored validation results for process_id: {process_id}")
  
    logging.info("Validation completed for all processes.")     
        
  except Exception as e:
    logging.error(f"Error in validating processes: {e}")
    raise ValueError(f"Error in validating processes: {e}")
