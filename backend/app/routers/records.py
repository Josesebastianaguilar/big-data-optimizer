from fastapi import APIRouter, Request, HTTPException, Depends
from app.utils.auth_utils import get_current_user
from app.models.record import Record
from app.utils.general_utils import get_query_params
from app.database import db
from bson.objectid import ObjectId

router = APIRouter()

@router.get("/{repository_id}")
async def get_records(request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get records for a specific repository.
    """
    parameters = get_query_params(request)
    query_params["repository"] = repository_id
    records = await db["repositories"].find(parameters["query_params"]).skip(parameters["offset"]).limit(parameters["limit"]).to_list(length=None)

    return {"records": records}

@router.post("/")
async def create_record(record: Record, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Create a new record in the database.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create a record")
    
    repository = await db["repositories"].find_one({"_id": ObjectId(record.repository)})
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository["processed_data"] is not True:
        raise HTTPException(status_code=500, detail="Repository data has not been processed")

    new_record = await db["records"].insert_one(record.dict())
    
    if not new_record:
        raise HTTPException(status_code=500, detail="Failed to create record")
    
    return {"record": new_record}
