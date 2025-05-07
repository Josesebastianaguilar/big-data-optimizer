from fastapi import APIRouter, Request, HTTPException, Depends
from app.utils.auth_utils import get_current_user
from app.models.record import Record
from app.models.process import Process, ProcessName, Trigger, ProcessingStatus
from app.utils.general_utils import get_query_params, validate_processes, validate_columns, validate_operator, validate_aggregation, validate_columns_types
from app.utils.user_initiated_processing_utils import start_user_initiated_process
from app.utils.repositories_utils import get_repository
from app.database import db
from bson.objectid import ObjectId
from datetime import datetime
import asyncio

router = APIRouter()

@router.get("/{process_id}")
async def get_process(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get a specific process by its process_id.
    """
    processes = await db["processes"].find({"process_id": ObjectId(process_id)})
    
    return {"process": process}

@router.post("/")
async def process_data(request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    body = await request.json()
    validate_processes(body["processes"].keys())
    repository = await get_repository(body["repository"])
    is_active_filtering_processing = body["processes"][ProcessName.FILTER] and body["processes"][ProcessName.FILTER]["active"] is True
    is_active_grouping_processing = body["processes"][ProcessName.GROUP] and body["processes"][ProcessName.GROUP]["active"] is True
    is_active_aggregation_processing = body["processes"][ProcessName.AGGREGATION] and body["processes"][ProcessName.AGGREGATION]["active"] is True
    all_processes = [ProcessName.FTILTER if is_active_filtering_processing else None, ProncessName.GROUP if is_active_grouping_processing else None, ProcessName.AGGREGATION if is_active_aggregation_processing else None]
    all_processes = [process for process in all_processes if process is not None]

    if all_processes == []:
        raise HTTPException(status_code=400, detail="No processes to execute")

    column_names = [col["name"] for col in repository["parameters"]]
    filter_columns = [col["name"] for col in body["processes"][ProcessName.FILTER]["columns"]] if is_active_filtering_processing else []
    group_by_columns = [col["name"] for col in body["processes"][ProcessName.GROUP]["columns"]] if is_active_grouping_processing  else []
    aggregation_columns = [col["name"] for col in body["processes"][ProcessName.AGGREGATION]["columns"]] if is_active_aggregation_processing else []
    aggregation_functions_names = [col["name"] for col in body["processes"][ProcessName.AGGREGATION]["columns"]] if is_active_aggregation_processing else []
    filter_conditions = body["processes"][ProcessName.FILTER]["columns"] if is_active_filtering_processing else []
    validate_columns(column_names, filter_columns)
    validate_columns(column_names, group_by_columns)
    validate_columns(column_names, aggregation_columns)
    
    for condition in filter_conditions:            
        filter_column = next((parameter for parameter in repository["parameters"] if parameter["name"] == condition["name"]), None)
        validate_operator(condition["operator"], filter_column["type"] if filter_column else "")
    
    validate_aggregation(aggregation_functions_names)
    validate_columns_types(repository["parameters"], body["processes"][ProcessName.AGGREGATION]["columns"] if is_active_aggregation_processing else [], "number")
    processes_optimized = []
    processes_non_optimized = []
    process_id = ObjectId()

    if is_active_filtering_processing:
        base_filter_process = {"parameters": filter_conditions, "actions": all_processes, "task_process": ProcessName.FILTER, "status": ProcessingStatus.PENDING, "repository": repository["_id"], "process_id": process_id, "trigger_type": Trigger.USER, "created_at": datetime.now(), "updated_at": datetime.now(), "iteration": 1, "repository_version": repository["version"]}

        processes_non_optimized.append({**base_filter_process, "optimized": False})
        processes_optimized.append({**base_filter_process, "optimized": True})
    
    if is_active_grouping_processing:
        base_group_process = {"parameters": body["processes"][ProcessName.GROUP]["columns"], "actions": all_processes, "task_process": ProcessName.GROUP, "status": ProcessingStatus.PENDING, "repository": repository["_id"], "process_id": process_id, "trigger_type": Trigger.USER, "created_at": datetime.now(), "updated_at": datetime.now(), "iteration": 1, "repository_version": repository["version"]}

        processes_non_optimized.append({**base_group_process, "optimized": False})
        processes_optimized.append({**base_group_process, "optimized": True})

    if is_active_aggregation_processing:
        base_aggregation_process = {"parameters": body["processes"][ProcessName.AGGREGATION]["columns"], "actions": all_processes, "task_process": ProcessName.AGGREGATION, "status": ProcessingStatus.PENDING, "repository": repository["_id"], "process_id": process_id, "trigger_type": Trigger.USER, "created_at": datetime.now(), "updated_at": datetime.now(), "iteration": 1, "repository_version": repository["version"]}

        processes_non_optimized.append({**base_aggregation_process, "optimized": False})
        processes_optimized.append({**base_aggregation_process, "optimized": True})
    
    try:
        await db["processes"].insert_many(processes_non_optimized + processes_optimized)
        asyncio.create_task(start_user_initiated_process(process_id, repository["_id"], all_processes))

        return {"message": "Processes started successfully", "process_id": str(process_id), "iteration": 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting processes: {e}")

@router.post("/iterate/{process_id}")
async def iterate_process(process_id: str, request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Iterate a specific process by its process_id.
    """
    body = await request.json()
    validate_processes(body["processes"].keys())
    repository = await get_repository(body["repository"])
    current_iteration = body["current_iteration"] or 1
    if current_iteration < 1:
        raise HTTPException(status_code=400, detail="Invalid iteration number")
    
    to_iterate_processes = await db["processes"].find({"process_id": ObjectId(process_id), "trigger_type": Trigger.USER, "repository": repository["_id"], "repository_version": repository["version"], "status": {"$ne": ProcessingStatus.PENDING}, "iteration": current_iteration + 1}, {"results": 0, "metrics": 0}).to_list(length=None)
    
    if len(to_iterate_processes) != 0:
        raise HTTPException(status_code=400, detail="Processes already iterated")
    
    processes = await db["processes"].find({"process_id": ObjectId(process_id), "trigger_type": Trigger.USER, "repository": repository["_id"], "repository_version": repository["version"], "status": {"$ne": ProcessingStatus.PENDING}, "iteration": current_iteration}, {"results": 0, "metrics": 0}).to_list(length=None)
    
    if len(processes) == 0:
        raise HTTPException(status_code=404, detail="Processes not found")
    
    new_iteration_processes = []
    actions = []
    for process in processes:
        if actions == []:
            actions = process["actions"]
        new_iteration_processes.append({
            "parameters": process["parameters"],
            "actions": process["actions"],
            "task_process": process["task_process"],
            "status": ProcessingStatus.PENDING,
            "repository": repository["_id"],
            "process_id": process_id,
            "trigger_type": Trigger.USER,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "optimized": process["optimized"],
            "iteration": process["iteration"] + 1
        })
    try:
        await db["processes"].insert_many(new_iteration_processes)
        asyncio.create_task(start_user_initiated_process(process_id, repository["_id"], actions, current_iteration + 1))
        
        return {"message": "Process iteration started successfully", "process_id": str(process_id), "iteration": current_iteration + 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iterating process: {e}")
