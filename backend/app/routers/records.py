from fastapi import APIRouter, Response, Request, HTTPException, Depends
from app.utils.auth_utils import get_current_user
from typing import List, Any
from app.models.record import Record
from app.utils.general_utils import get_query_params
from app.utils.records_utils import validate_permissions_and_repository, update_repository_info
from app.database import db
from bson.objectid import ObjectId
from datetime import datetime

router = APIRouter()

@router.get("/{repository_id}")
async def get_records(request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get records for a specific repository.
    """
    try:
        parameters = get_query_params(request)
        query_params["repository"] = repository_id
        records = await db["repositories"].find(parameters["query_params"]).skip(parameters["offset"]).limit(parameters["limit"]).to_list(length=None)
        
        return Response(status_code=200, content={"records": records})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching records: {str(e)}")


@router.put("/")
async def update_record(record: Record, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Update a record in the database.
    """
    try:
        repository = await db["repositories"].find_one({"_id": ObjectId(record.repository)})
        
        validate_permissions_and_repository(current_user, repository)
        now = datetime.now()

        await db["records"].update_one({"_id": ObjectId(record.id)}, {"$set": {**record.dict(), "updated_at": now, version: repository.version + 1}})
        
        await update_repository_info(repository)
    
        return Response(status_code=200, content={"_id": record["_id"] ,"message": "Record updated successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating record: {str(e)}")

    

@router.post("/")
async def create_record(record: Record, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Create a new record in the database.
    """
    try:

        repository = await db["repositories"].find_one({"_id": ObjectId(record.repository)})
    
        validate_permissions_and_repository(current_user, repository)
        now = datetime.now()

        new_record = await db["records"].insert_one({**record.dict(), "created_at": now, "updated_at": now, version: repository.version + 1})

        await update_repository_info(repository)
    
        return Response(status_code=201, content={"id": str(new_record.inserted_id), "message": "Record created successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")

@router.delete("/{record_id}")
async def delete_record(record_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Delete a record from the database.
    """
    try:
        record = await db["records"].find_one({"_id": ObjectId(record_id)})
        
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        repository = await db["repositories"].find_one({"_id": ObjectId(record.repository)})
        
        validate_permissions_and_repository(current_user, repository)
        
        await db["records"].delete_one({"_id": ObjectId(record_id)})
        
        await update_repository_info(repository)
    
        return Response(status_code=200, content={"_id": record["_id"], "message": "Record deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting record: {str(e)}")
    
