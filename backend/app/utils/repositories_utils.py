import pandas as pd
import mimetypes
import logging
import os
import json
from fastapi import Request, Response, HTTPException
from typing import List
from app.database import db, recreate_records_indexes_from_repositories
from bson.objectid import ObjectId
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "50"))  # Default to 50MB

def validate_repository_file(repository: dict):
    if repository["file"] is None and repository["large_file"] is True and repository["file_path"] is None:
        raise HTTPException(status_code=400, detail="Must specify file_path for large files.")
            
    if repository["file"] is not None and repository["file"].size > MAX_FILE_SIZE * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit. Please use large file upload.")

    if repository["file"] and repository["file"].content_type != "text/csv":
        mime_type, _ = mimetypes.guess_type(repository["file"].filename)
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
    if "file" not in repository and repository["large_file"] is True:
        file_path = Path(repository["file_path"])

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=400, detail="File does not exist or is not a file.")

        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type != "text/csv":
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

async def upsert_repository(repository_id, name, description, url, large_file, file_path, file, parameters, current_user: dict, upsert_type: str) -> dict:
    """Upsert a repository."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    repository = {"name": name, "description": description, "url": url, "large_file": large_file, "file_path": file_path, "file": file}

    if upsert_type == "create":
        if repository["file"] is None and repository["large_file"] is not True:
            raise HTTPException(status_code=400, detail="File is required for new repositories.")
        
        try:
            validate_repository_file(repository)
            now = datetime.now()
            repository_data = {"name": repository["name"], "description": repository["description"], "url": repository["url"], "version": 0, "data_ready": False, "valid": False, "created_at": now, "updated_at": now}
            result = await db["repositories"].insert_one(repository_data)
            if "file" in repository and repository["file"] is not None:
                file_name = f"{repository['name'].replace(' ', '_')}_{datetime.now().timestamp()}.csv"
                file_path = os.path.join(UPLOAD_DIR, file_name)
                with open(file_path, "wb") as f:
                    while chunk := await repository["file"].read(1024 * 1024):  # 1MB chunks
                        if not chunk:
                            break
                        f.write(chunk)
                repository["file_path"] = file_name
                repository["large_file"] = True
                repository["file"] = None
                
            repository["_id"] = str(result.inserted_id)
            
            await db["jobs"].insert_one({"type": "store_repository_records", "data": {"repository": repository, "delete_existing_records": False}})

            return Response(status_code=201, content=json.dumps({"id": str(repository["_id"]), "message": "Repository created successfully"}), media_type="application/json")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error insertincreatingg repository: {str(e)}")
    
    elif upsert_type == "update":
        validate_repository_file(repository)
        now = datetime.now()
        repository_data = {"name": repository["name"], "description": repository["description"], "url": repository["url"], "version": 0, "updated_at": now, "parameters": parameters}
        if ("file" in repository and repository["file"] is not None) or repository["large_file"] is True:
            print("Has file")
            repository_data["parameters"] = []
            repository_data["data_ready"] = False
            repository_data["valid"] = False
            repository_data["file_size"] = None
            repository_data["original_data_size"] = None
            repository_data["current_data_size"] = None
            repository_data["data_updated_at"] = None
            repository["_id"] = repository_id

        try:
            result = await db["repositories"].update_one({"_id": ObjectId(repository_id)}, {"$set": repository_data})
            if "file" not in repository or repository["file"] is None:
                await db["jobs"].insert_one({"type": "reset_indexes", "data": {}})
            
            if "file" in repository and repository["file"] is not None:
                file_name = f"{repository['name'].replace(' ', '_')}_{datetime.now().timestamp()}.csv"
                file_path = os.path.join(UPLOAD_DIR, file_name)
                with open(file_path, "wb") as f:
                    while chunk := await repository["file"].read(1024 * 1024):  # 1MB chunks
                        if not chunk:
                            break
                        f.write(chunk)
                repository["file_path"] = file_name
                repository["large_file"] = True
                repository["file"] = None
            
            if ("file" in repository and repository["file"] is not None) or repository["large_file"] is True:
                await db["jobs"].insert_one({"type": "store_repository_records", "data": {"repository": repository, "delete_existing_records": True}})
            
            return Response(status_code=200, content=json.dumps({"id": str(repository_id), "message": "Repository updated successfully"}), media_type="application/json")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating repository: {str(e)}")
        
async def get_repository(repository_id: str) -> dict:
    """
    Validate if the repository exists and is not processed.
    """
    repository = await db["repositories"].find_one({"_id": ObjectId(repository_id)})
    
    if not repository:
        logging.error(f"Repository with ID {repository_id} not found.")
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository["data_ready"] is not True:
        logging.error(f"Repository with ID {repository_id} has not been processed yet.")
        raise HTTPException(status_code=500, detail="Data has been not prepared yet")
    
    if repository["current_data_size"] is None or repository["current_data_size"] == 0:
        logging.error(f"Repository with ID {repository_id} has no records.")
        raise HTTPException(status_code=500, detail="Repository has no records")
    
    return repository
