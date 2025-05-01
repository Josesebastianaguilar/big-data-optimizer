from bson.objectid import ObjectId
from app.models.process import Process, ProcessingStatus, ProcessName
from fastapi import BackgroundTasks
from typing import List
from app.database import db
import utils.non_optimized_processing_utils as non_opt_utils
import utils.optimized_processing_utils as opt_utils
import pandas as pd
import multiprocessing as mp
import time



async def filter_non_optimized_data(df: pd.DataFrame, filters: List[dict], process: Process) -> pd.DataFrame:
  
  return non_opt_utils.filter_data(df: pd.DataFrame, process["parameters"])
    

def filter_optimized_()

async def process_data(df: pd.DataFrame, processes: List[Process], actions: List[ProcessName], num_processes, processing_utils, type):
  if ProcessName.FILTER in actions:
    input_filter_data_size = len(df)
    filter_start_time = time.perf_counter()
    filter_process = next((process for process in processes if process["task_process"] == ProcessName.FILTER), None)
    await db["processes"].update_one({"_id": filter_process["_id"]}, {"$set": {"start_time": filter_start_time, "input_data_size": input_filter_data_size, "updated_at": filter_start_time}})
    result = None
    try:
      filter_results = processing_utils.filter_data(df, process[0]["parameters"], max(num_processes - 1, 1))
      filter_end_time = time.perf_counter()
      output_filter_data_size = len(filter_results)
      filter_duration = (filter_end_time - filter_start_time)
      await db["processes"].update_one({"_id": filter_process["_id"]}, {"$set": {"results": filter_results.to_dict("records"), "end_time": filter_end_time, "duration": filter_duration, "output_data_size": output_filter_data_size, "updated_at": filter_end_time}})
      if ProcessName.GROUP in actions and ProcessName.AGGREGATION in actions: 

      else if ProcessName.GROUP in actions:

      else if ProcessName.AGGREGATION in actions:
    except Exception as e:
      filter_end_time = time.perf_counter()
      filter_duration = (filter_end_time - filter_start_time)
      await db["processes"].update_one({"_id": filter_process["_id"]}, {"$set": {"errors": e, "end_time": filter_end_time, "duration": filter_duration, "updated_at": filter_end_time}})
  else if ProcessName.GROUP in actions and ProcessName.AGGREGATION in actions: 

  else if ProcessName.GROUP in actions:

  else if ProcessName.AGGREGATION in actions:
  

async def process_sequential_non_optimized_data(df: pd.DataFrame, processes: List[Process], actions: List[ProcessName], num_processes):
  data_list = df["data"].tolist()
  processing_utils = non_opt_utils
  
  

def process_sequential_optimized_data(df: pd.DataFrame, processes: List[Process], actions: List[ProcessName], num_processes):

async def process_sequential_data(process_id: ObjectId, repository_id: ObjectId, actions: List[ProcessName]):
    """
    Process data for a given collection and queries.
    """
    # Fetch data from the database
    records = db["records"].find({"repository": repository_id})
    processes = db["processes"].find({"process_id": process_id})
    optimized_processes = processes.filter(lambda process: process["optimized"] is True)
    non_optimized_processes = processes.filter(lambda process: process["optimized"] is False)
    df = pd.DataFrame(records)
    num_processes = mp.cpu_count()
    functions = [
        process_sequential_non_optimized_data,
        process_sequential_optimized_data
    ]
    args = [
        (df, non_optimized_processes, actions, max(num_processes - 1, 1)),
        (df, optimized_processes, actions, max(num_processes - 1, 1))
    ]
    with mp.Pool(processes=num_processes) as pool:
        pool.starmap(lambda f, a: f(*a), zip(functions, args))
