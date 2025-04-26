from fastapi import Request
from typing import List, Any
from app.database import db
from app.models.repository import Repository
import pandas as pd


async def process_repository_data(repository_id: str):
    repository = await db["repositories"].find_one({"_id": ObjectId(repository_id)})
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.get("processed_data") is True:
        return {"message": "Data already processed"}
    
    if not hasattr(repository, 'file'):
        raise HTTPException(status_code=500, detail="File not found")
    
    # Process the repository data here from the repository file that is a csv file
    file_content = await repository.file.read()
    csv_data = pd.read_csv(BytesIO(file_content))
    records = csv_data.to_dict(orient="records")
    record_promises = [{"repository": repository["_id"], "data": record} for record in records]
    try:
        await db["records"].insert_many(record_promises)
        await db["repository"].update_one({"_id": ObjectId(repository_id)}, {"$set": {"processed_data": True}})

    except Exception as e:
        raise ValueError(f"Error processing repository data: {e}")




    