from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from app.utils.auth_utils import get_current_user
from app.models.record import Record
from app.models.process import Process, ProcessName, ProcessingType, ProcessingStatus
from app.utils.general_utils import get_query_params, validate_processes, validate_columns, validate_operator, validate_aggregation, validate_columns_types
from app.utils.processes_utils import process_sequential_data
from app.database import db
from bson.objectid import ObjectId
from datetime import datetime

router = APIRouter()

async def get_repository(repository_id: str) -> dict:
    """
    Validate if the repository exists and is not processed.
    """
    repository = await db["repositories"].find_one({"_id": ObjectId(repository_id)})
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.get("processed_data") is not True:
        raise HTTPException(status_code=500, detail="Data has been not ")
    
    return repository



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
    column_names = [col["name"] for col in repository["parameters"]]
    filter_columns = [col["name"] for col in body["processes"][ProcessName.FILTER]["columns"]] if body["processes"][ProcessName.FILTER] and body["processes"][ProcessName.FILTER]["active"] is True else []
    group_by_columns = [col["name"] for col in body["processes"][ProcessName.GROUP]["columns"]] if body["processes"][ProcessName.GROUP] and body["processes"][ProcessName.GROUP]["active"] is True  else []
    aggregation_columns = [col["name"] for col in body["processes"][ProcessName.AGGREGATE]["columns"]] if body["processes"][ProcessName.AGGREGATE] and body["processes"][ProcessName.AGGREGATE]["active"] is True else []
    aggregation_functions_names = [col["name"] for col in body["processes"][ProcessName.AGGREGATE]["columns"]] if body["processes"][ProcessName.AGGREGATE] and body["processes"][ProcessName.AGGREGATE]["active"] is True else []
    filter_conditions = body["processes"][ProcessName.FILTER]["columns"] if body["processes"][ProcessName.FILTER] and body["processes"][ProcessName.FILTER]["active"] is True else []
    processes_actions = []
    validate_columns(column_names, filter_columns)
    validate_columns(column_names, group_by_columns)
    validate_columns(column_names, aggregation_columns)
    
    for condition in filter_conditions:            
        filter_column = next((parameter for parameter in repository["parameters"] if parameter["name"] == condition["name"]), None)
        validate_operator(condition["operator"], filter_column["type"] if filter_column else "")
    
    validate_aggregation(aggregation_functions_names)
    validate_columns_types(repository["parameters"], body["processes"][ProcessName.AGGREGATE]["columns"] if body["processes"][ProcessName.AGGREGATE] and body["processes"][ProcessName.AGGREGATE]["active"] is True else [], "number")
    
    processes_optimized = []
    processes_non_optimized = []

    process_id = ObjectId()

    if body["processes"][ProcessName.FILTER] and body["processes"][ProcessName.FILTER]["active"] is True
        processes_actions.append(ProcessName.FILTER)
        base_filter_process = {"parameters": filter_conditions, "task_process": ProcessName.FILTER, "status": ProcessingStatus.PENDING, "repository": repository["_id"], "process_id": process_id, "process_type": ProcessingType.SEQUENTIAL, "created_at": datetime.now(), "updated_at": datetime.now()}

        processes_non_optimized.append({**base_filter_process, "optimized": False})
        processes_optimized.append({**base_filter_process, "optimized": True})
    
    if body["processes"][ProcessName.GROUP] and body["processes"][ProcessName.GROUP]["active"] is True
        processes_actions.append(ProcessName.GROUP)
        base_group_process = {"parameters": body["processes"][ProcessName.GROUP]["columns"], "task_process": ProcessName.GROUP, "status": ProcessingStatus.PENDING, "repository": repository["_id"], "process_id": process_id, "process_type": ProcessingType.SEQUENTIAL, "created_at": datetime.now(), "updated_at": datetime.now()}

        processes_non_optimized.append{**base_group_process, "optimized": False})
        processes_optimized.append({**base_group_process, "optimized": True})

    if body["processes"][ProcessName.AGGREGATE] and body["processes"][ProcessName.AGGREGATE]["active"] is True
        processes_actions.append(ProcessName.AGGREGATE)
        base_aggregation_process = {"parameters": body["processes"][ProcessName.AGGREGATE]["columns"], "task_process": ProcessName.AGGREGATE, "status": ProcessingStatus.PENDING, "repository": repository["_id"], "process_id": process_id, "process_type": ProcessingType.SEQUENTIAL, "created_at": datetime.now(), "updated_at": datetime.now()}

        processes_non_optimized.append({**base_aggregation_process, "optimized": False})
        processes_optimized.append({**base_aggregation_process, "optimized": True})
    
    try:
        await db["processes"].insert_many(processes_non_optimized + processes_optimized)
        background_tasks = BackgroundTasks()
        background_tasks.add_task(process_sequential_data, process_id, repository["_id"], processes_actions)

        return {"message": "Processes started successfully", "process_id": str(process_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting processes: {e}")

