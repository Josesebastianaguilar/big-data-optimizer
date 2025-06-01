from fastapi import APIRouter, Response, Request, HTTPException, Depends
from app.utils.auth_utils import get_current_user
from typing import List, Any
from app.models.record import Record
from app.utils.general_utils import get_query_params
from app.utils.records_utils import validate_permissions_and_repository, update_repository_info
from app.database import db
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime

router = APIRouter()

@router.get("/{repository_id}")
async def get_records(repository_id: str, request: Request) -> dict:
    """
    Get records for a specific repository.
    """
    try:
        repository = await db["repositories"].find_one({"_id": ObjectId(repository_id)}, {"current_data_size": 1})
        if not repository:
            raise HTTPException(status_code=404, detail=f"Repository {repository_id} not found")
        
        parameters = get_query_params(request)
        parameters["query_params"]["repository"] = ObjectId(repository_id)
        totalItems = 0
        if "_id" in parameters["query_params"]:
            totalItems = await db["records"].count_documents(parameters["query_params"])
        else:
            totalItems = repository["current_data_size"]
        page = parameters["page"]
        totalPages = totalItems // parameters["limit"] + (1 if totalItems % parameters["limit"] > 0 else 0)
        
        records = await db["records"].find(parameters["query_params"], parameters["select"]).skip(parameters["offset"]).limit(parameters["limit"]).to_list(length=None)
        
        return Response(status_code=200, content=json_util.dumps({"totalItems": totalItems, "totalPages": totalPages, "page": page, "items": records}), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching records: {str(e)}")


@router.put("/{record_id}")
async def update_record(record_id: str, request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Update a record in the database.
    """
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to update records")
        
        record = await request.json()
        current_record = await db["records"].find_one({"_id": ObjectId(record_id)})
        
        if not current_record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        repository = await db["repositories"].find_one({"_id": ObjectId(current_record["repository"])})
        
        validate_permissions_and_repository(current_user, repository, record)
        now = datetime.now()

        await db["records"].update_one({"_id": ObjectId(record_id)}, {"$set": {"data": {**record}, "updated_at": now, "version": repository["version"] + 1}})
        
        await update_repository_info(repository, "update")
    
        return Response(status_code=200, content=json_util.dumps({"_id": record_id ,"message": "Record updated successfully"}), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating record: {str(e)}")

    

@router.post("/{repository_id}")
async def create_record(repository_id: str, request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Create a new record in the database.
    """
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to update records")
        
        record = await request.json()

        repository = await db["repositories"].find_one({"_id": ObjectId(repository_id)})
    
        validate_permissions_and_repository(current_user, repository, record)
        now = datetime.now()

        new_record = await db["records"].insert_one({"data": {**record}, "created_at": now, "repository": ObjectId(repository_id), "updated_at": now, "version": repository["version"] + 1})

        await update_repository_info(repository, "create")
    
        return Response(status_code=201, content=json_util.dumps({"id": str(new_record.inserted_id), "message": "Record created successfully"}), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")

@router.delete("/{record_id}")
async def delete_record(record_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Delete a record from the database.
    """
    try:
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="You do not have permission to update records")
        
        record = await db["records"].find_one({"_id": ObjectId(record_id)})
        
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        repository = await db["repositories"].find_one({"_id": record["repository"]})
        
        validate_permissions_and_repository(current_user, repository, None)
        
        await db["records"].delete_one({"_id": ObjectId(record_id)})
        
        await update_repository_info(repository, "delete")
    
        return Response(status_code=200, content=json_util.dumps({"_id": record["_id"], "message": "Record deleted successfully"}), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")
    
