from fastapi import HTTPException
from app.database import db
from datetime import datetime
from typing import Any

def validate_permissions_and_repository(current_user: dict, repository: Any, record: dict):
    """
    Validate the record before creating or updating one at the database.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository["data_ready"] is not True:
        raise HTTPException(status_code=500, detail="Repository data has not been prepared yet")
    
    if record is not None:
        parameter_names = [param["name"] for param in repository["parameters"]]
        for param in repository["parameters"]:
            if record[param["name"]] is None or not record[param["name"]] or record[param["name"]] == "" :
                raise HTTPException(status_code=400, detail=f"Field '{param['name']}' is required")
            if param["type"] == "number":
                if not isinstance(record[param["name"]], (int, float)):
                    raise HTTPException(status_code=400, detail=f"Field '{param['name']}' must be a number")
            elif param["type"] == "string":
                if not isinstance(record[param["name"]], str):
                    raise HTTPException(status_code=400, detail=f"Field '{param['name']}' must be a string")
        
        record_keys = record.keys()
        
        for key in record_keys:
            if key not in parameter_names:
                raise HTTPException(status_code=400, detail=f"Invalid field '{key}' in record. Allowed fields are: {', '.join(parameter_names)}") 

async def update_repository_info(repository: Any, type: str):
    records_count = 0
    
    if type == "create":
        records_count = repository["current_data_size"] + 1
    elif type == "update":
        records_count = repository["current_data_size"]
    elif type == "delete":
        records_count = repository["current_data_size"] - 1
        
        
    now = datetime.now()
    repository_data = {"current_data_size": records_count, "data_updated_at": now, "updated_at": now, "version": repository["version"] + 1}
    
    await db["repositories"].update_one({"_id": repository["_id"]}, {"$set": repository_data})
    