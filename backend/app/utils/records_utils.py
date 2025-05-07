from fastapi import HTTPException
from app.database import db
from datetime import datetime

def validate_permissions_and_repository(current_user: dict, repository: Any):
    """
    Validate the record before creating or updating one at the database.
    """
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository["data_ready"] is not True:
        raise HTTPException(status_code=500, detail="Repository data has not been processed")

async def update_repository_info(repository: Any):
    records_count = await db["records"].count_documents({"repository": repository["_id"]})
    now = datetime.now()
    repository_data = {"current_data_size": records_count, "data_updated_at": now "updated_at": now, verion: repository["version"] + 1}
    
    await db["repositories"].update_one({"_id": repository["_id"]}, {"$set": repository_data})
    