from fastapi import APIRouter, Response, Request, HTTPException, Depends
from app.utils.auth_utils import get_current_user
from app.models.record import Record
from app.utils.general_utils import get_query_params, validate_processes, validate_parameters, validate_operator, validate_aggregations, validate_aggregation_parameter_types
from app.utils.repositories_utils import get_repository
from app.database import db
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime
from dotenv import load_dotenv
import logging

router = APIRouter()

@router.get("/{repository_id}")
async def get_processes(repository_id: str, request:Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get a specific process by its process_id.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    parameters = get_query_params(request)
    parameters["query_params"]["repository"] = ObjectId(repository_id)
    # parameters["query_params"]["trigger_type"] = Tigger.USER
    totalItems = await db["processes"].count_documents(parameters["query_params"])
    page = parameters["page"]
    totalPages = totalItems // parameters["limit"] + (1 if totalItems % parameters["limit"] > 0 else 0)
    
    processes = await db["processes"].find(parameters["query_params"], parameters["select"]).skip(parameters["offset"]).limit(parameters["limit"]).to_list(length=None)
    
    return Response(status_code=200, content=json_util.dumps({"totalItems": totalItems, "totalPages": totalPages, "page": page, "items": processes}), media_type="application/json")

@router.post("/{repository_id}")
async def process_data(repository_id: str, request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    existing_executing_processes = await db["processes"].find({"status": "in_progress"}, {"results": 0, "metrics": 0, "errors": 0}).to_list(length=None)
        
    if len(existing_executing_processes) > 0:
        logging.error(f"There are executing processes. Please try again later")
        raise HTTPException(status_code=500, detail=f"There are executing processes. Please try again later")
    
    process_id = ObjectId()
    body = await request.json()
    validate_processes(body.keys())
    repository = await get_repository(repository_id)
    is_active_filtering_processing = True if body["filter"] and body["filter"]["active"] else False
    is_active_grouping_processing = True if body["group"] and body["group"]["active"] else False
    is_active_aggregation_processing = True if body["aggregation"] and body["aggregation"]["active"] else False
    all_processes = ["filter" if is_active_filtering_processing else None, "group" if is_active_grouping_processing else None, "aggregation" if is_active_aggregation_processing else None]
    all_processes = [process for process in all_processes if process is not None]

    if all_processes == []:
        logging.error(f"No Processes to execute for repository {body['repository']}")
        raise HTTPException(status_code=400, detail="No processes to execute")
    

    parameter_names = [parameter["name"] for parameter in repository["parameters"]]
    filter_parameters = body["filter"]["parameters"] if is_active_filtering_processing else []
    filter_parameter_names = [parameter["name"] for parameter in filter_parameters]
    group_by_parameters = body["group"]["parameters"] if is_active_grouping_processing else []
    aggregation_parameters = body["aggregation"]["parameters"] if is_active_aggregation_processing else []
    aggregation_parameter_names = [parameter["name"] for parameter in aggregation_parameters]
    operations = [parameter["operations"] for parameter in aggregation_parameters]
    validate_parameters(parameter_names, filter_parameter_names)
    validate_parameters(parameter_names, group_by_parameters)
    validate_parameters(parameter_names, aggregation_parameter_names)
    
    for parameter in filter_parameters: 
        repository_parameter = next((param for param in repository["parameters"] if param["name"] == parameter["name"]), None)           
        validate_operator(repository_parameter, parameter["operator"], parameter["value"])
    
    for operation in operations:
        validate_aggregations(operation)
    validate_aggregation_parameter_types(repository["parameters"], aggregation_parameter_names, "number")
    processes_optimized = []
    processes_non_optimized = []

    if is_active_filtering_processing:
        base_filter_process = {"parameters": filter_parameters, "actions": all_processes, "task_process": "filter", "status": "in_progress", "repository": repository["_id"], "process_id": process_id, "trigger_type": "user", "created_at": datetime.now(), "updated_at": datetime.now(), "iteration": 1, "repository_version": repository["version"], "validated": False}

        processes_non_optimized.append({**base_filter_process, "optimized": False})
        processes_optimized.append({**base_filter_process, "optimized": True})
    
    if is_active_grouping_processing:
        base_group_process = {"parameters": group_by_parameters, "actions": all_processes, "task_process": "group", "status": "in_progress", "repository": repository["_id"], "process_id": process_id, "trigger_type": "user", "created_at": datetime.now(), "updated_at": datetime.now(), "iteration": 1, "repository_version": repository["version"], "validated": False}

        processes_non_optimized.append({**base_group_process, "optimized": False})
        processes_optimized.append({**base_group_process, "optimized": True})

    if is_active_aggregation_processing:
        base_aggregation_process = {"parameters": aggregation_parameters, "actions": all_processes, "task_process": "aggregation", "status": "in_progress", "repository": repository["_id"], "process_id": process_id, "trigger_type": "user", "created_at": datetime.now(), "updated_at": datetime.now(), "iteration": 1, "repository_version": repository["version"], "validated": False}

        processes_non_optimized.append({**base_aggregation_process, "optimized": False})
        processes_optimized.append({**base_aggregation_process, "optimized": True})
    try:    
        await db["processes"].insert_many(processes_non_optimized + processes_optimized)
        await db["jobs"].insert_one({"type": "start_process", "data": {"process_id": str(process_id), "repository_id": str(repository_id), "actions": all_processes, "iteration": 1, "trigger_type": "user"}})
        
        return Response(status_code=200, content=json_util.dumps({"process_id": str(process_id), "iteration": 1, "message": "Process started successfully"}), media_type="application/json")
    except Exception as e:
        logging.error(f"Error starting process for repository {repository_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting process: {e}")

@router.post("/iterate/{process_id}")
async def iterate_process(process_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Iterate a specific process by its process_id.
    """
    try:
        existing_executing_processes = await db["processes"].find({"status": "in_progress"}, {"results": 0, "metrics": 0, "errors": 0}).to_list(length=None)
        
        if len(existing_executing_processes) > 0:
            logging.error(f"There are executing processes. Please try again later")
            raise HTTPException(status_code=500, detail=f"There are executing processes. Please try again later")
            
        existing_processes = await db["processes"].find({"process_id": ObjectId(process_id), "trigger_type": "user", "status": {"$ne": "in_progress"}}, {"results": 0, "metrics": 0, "errors": 0}).to_list(length=None)
        if len(existing_processes) == 0:
            logging.error(f"Processes not found for the given process_id: {process_id}")
            raise HTTPException(status_code=400, detail="Processes not found for the given process_id. Not possible to iterate.")
        
        repository = await get_repository(str(existing_processes[0]["repository"]))
        if repository["version"] != existing_processes[0]["repository_version"]:
            logging.error(f"Repository version mismatch for repository {repository['_id']}. Current version: {repository['version']}, Process version: {existing_processes[0]['repository_version']}")
            raise HTTPException(status_code=400, detail="Repository version mismatch. Not possible to iterate.")
        iterations = [process["iteration"] for process in existing_processes]
        current_iteration = max(iterations) if len(iterations) > 0 else None
        if current_iteration is None:
            raise HTTPException(status_code=500, detail="There are inconsistencies in the process data. Iteration can not be set")    
        
        new_iteration_processes = []
        actions = []
        for process in existing_processes:
            if actions == []:
                actions = process["actions"]
                
            new_iteration_processes.append({
                "parameters": process["parameters"],
                "actions": process["actions"],
                "task_process": process["task_process"],
                "status": "in_progress",
                "repository": ObjectId(repository["_id"]),
                "repository_version": repository["version"],
                "process_id": ObjectId(process_id),
                "trigger_type": "user",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "optimized": process["optimized"],
                "iteration": current_iteration + 1,
                "validated": False
            })
        
        await db["processes"].insert_many(new_iteration_processes)
        await db["jobs"].insert_one({"type": "start_process", "data": {"process_id": str(process_id), "repository_id": str(repository["_id"]), "actions": actions, "iteration": current_iteration + 1, "trigger_type": "user"}})
        
        return Response(status_code=200, content=json_util.dumps({"process_id": process_id, "iteration": current_iteration + 1, "message": "Process iteration started successfully"}), media_type="application/json")
    except Exception as e:
        logging.error(f"Error iterating process {process_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error iterating process: {e}")

@router.put("/validate")
async def validate_processes_endpoint(request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Validate processes.
    """
    try:
        await db["jobs"].insert_one({"type": "validate_processes", "data": {}})
        
        return Response(status_code=201, content=json_util.dumps({"message": "validation_started"}), media_type="application/json")
    except Exception as e:
        logging.error(f"Error validating processes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating processes: {e}")

@router.delete("/{repository_id}")
async def reset_processes(repository_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Reset processes for a specific repository.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to reset processes")
    
    try:
        await db["jobs"].insert_one({"type": "reset_processes", "data": {"repository_id": repository_id}})
        
        return Response(status_code=200, content=json_util.dumps({"message": "Processes reset successfully"}), media_type="application/json")
    except Exception as e:
        logging.error(f"Error resetting processes for repository {repository_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting processes: {e}")