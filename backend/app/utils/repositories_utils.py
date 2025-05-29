import pandas as pd
import mimetypes
import logging
import os
import asyncio
import json
from fastapi import Request, Response, HTTPException
from typing import List, Any
from app.database import db, recreate_records_indexes_from_repositories
from app.models.repository import Repository
from pathlib import Path
from bson.objectid import ObjectId
from fastapi import UploadFile
from dotenv import load_dotenv
from datetime import datetime
from io import BytesIO


load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

async def store_repository_records(repository: Repository, parameters: List[dict], csv_data: pd.DataFrame, file_size: float, delete_existing_records: bool = False):
    if delete_existing_records:
        try:
            await db["records"].delete_many({"repository": ObjectId(repository['_id'])})
            await db["processes"].delete_many({"repository": ObjectId(repository['_id'])})
            logging.info(f"Deleted existing records and processes for repository {repository['_id']}")
        except Exception as e:
            logging.error(f"Error deleting existing records and processes for repository {repository['_id']}: {e}")
            raise ValueError(f"Error deleting existing records and processes for repository {repository['_id']}: {e}")
    try:
        now = datetime.now()
        csv_data = csv_data.where(pd.notnull(csv_data), None)
        records_data = csv_data.to_dict(orient="records")
        records = [{"repository": ObjectId(repository['_id']), "data": record, "created_at": now, "updated_at": now, "version": 0} for record in records_data]
        
        num_records = len(records)
        
        batch_size = 5000
        for i in range(0, num_records, batch_size):
            batch = records[i:i + batch_size]
            await db["records"].insert_many(batch)
            logging.info(f"Inserted {len(batch)} records for repository {repository['_id']}")
        
        logging.info(f"Inserted total {num_records} records for repository {repository['_id']}")

        repository_data = {
            "data_ready": True,
            "valid": True,
            "file_size": file_size,
            "type": "text/csv",
            "original_data_size": num_records,
            "current_data_size": num_records,
            "data_updated_at": datetime.now(),
            "parameters": parameters,
        }
        await db["repositories"].update_one({"_id": ObjectId(repository['_id'])}, {"$set": repository_data})
        logging.info(f"Updated repository {repository['_id']} with {num_records} records")
        if repository["large_file"] and repository["file_path"]:
            path = Path(f"{UPLOAD_DIR}/{repository['file_path']}")
            if path.exists():
                try:
                    path.unlink()
                    logging.info(f"Deleted file at {repository['file_path']}")
                except Exception as e:
                    logging.error(f"Error deleting file at {repository['file_path']}: {e}")
                    raise ValueError(f"Error deleting file at {repository['file_path']}: {e}")
            else:
                logging.warning(f"File at {repository['file_path']} does not exist")
        
        asyncio.create_task(recreate_records_indexes_from_repositories())
        

    except Exception as e:
        logging.error(f"Error storing records for repository {repository['_id']}: {e}")
        raise ValueError(f"Error storing records for repository {repository['_id']}: {e}")

def read_file_from_path(file_path: str) -> bytes:
    """
    Read the file content from the given file path.
    """
    path = Path(file_path)
    
    with path.open("rb") as file:
        return file.read()


async def process_file(repository: dict, delete_existing_records: bool = False) -> List[dict]:
    """Get parameters from the uploaded CSV file."""
    file_content = None

    if "file" in repository and repository["file"] is not None:
        file_content = repository["file"]
    elif repository.get("large_file") is True and repository["file_path"] is not None:
        file_content = read_file_from_path(f"{UPLOAD_DIR}/{repository['file_path']}")
    else:
        logging.error("No file or file_path provided for processing.")
        raise ValueError("No file or file_path provided for processing.")
    
    file_size = len(file_content) / (1024 * 1024)
    csv_data = pd.read_csv(BytesIO(file_content))
    column_names = list(csv_data.columns)
    complete_record = None
    
    for _, row in csv_data.iterrows():
        if row.notnull().all():
            complete_record = row
            break
    
    if complete_record is None:
        logging.error(f"No complete record found in the CSV file for repository {repository['_id']}")
        if not csv_data.empty:
            complete_record = csv_data.loc[csv_data.isnull().sum(axis=1).idxmin()]  # Row with the fewest nulls
        else:
            logging.error("The CSV file is empty. Aborting processing.")
            raise ValueError(f"The CSV file is empty and contains no valid records. at process_file for repository {repository['_id']}")
        
    
    parameters = []
    
    for col in column_names:
        value = complete_record[col]
        if isinstance(value, (int, float)):
            column_type = "number"
        elif isinstance(value, str):
            column_type = "string"
        else:
            column_type = "string"
        parameters.append({"name": col, "type": column_type})

    await store_repository_records(repository, parameters, csv_data, file_size, delete_existing_records)

def validate_repository_file(repository: dict):
    if repository["file"] is None and repository["large_file"] is True and repository["file_path"] is None:
        raise HTTPException(status_code=400, detail="Must specify file_path for large files.")
            
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
                file_content = await repository["file"].read()
                repository["file"] = file_content
                
            repository["_id"] = result.inserted_id
            asyncio.create_task(process_file(repository))

            return Response(status_code=201, content=json.dumps({"id": str(repository["_id"]), "message": "Repository created successfully"}), media_type="application/json")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error insertincreatingg repository: {str(e)}")
    
    elif upsert_type == "update":
        validate_repository_file(repository)
        now = datetime.now()
        repository_data = {"name": repository["name"], "description": repository["description"], "url": repository["url"], "version": 0, "updated_at": now, "parameters": parameters}
        if ("file" in repository and repository["file"] is not None) or repository["large_file"] is True:
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
                asyncio.create_task(recreate_records_indexes_from_repositories())
            
            if "file" in repository and repository["file"] is not None:
                file_content = await repository["file"].read()
                repository["file"] = file_content
            
            if ("file" in repository and repository["file"] is not None) or repository["large_file"] is True:
                asyncio.create_task(process_file(repository, True))
            
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


async def delete_collection_in_batches(collection, filter_query, batch_size=5000):
    while True:
        # Find a batch of _ids to delete
        ids = await collection.find(filter_query, {"_id": 1}).limit(batch_size).to_list(length=batch_size)
        if not ids:
            break
        id_list = [doc["_id"] for doc in ids]
        result = await collection.delete_many({"_id": {"$in": id_list}})
        if result.deleted_count < batch_size:
            break


async def delete_repository_related_data(repository_id: str):
    """
    Delete all records and processes related to the repository.
    """
    try:
        logging.info(f"Deleting all records and processes for repository {repository_id}")
        filter_query = {"repository": ObjectId(repository_id)}
        await delete_collection_in_batches(db["records"], filter_query)
        await delete_collection_in_batches(db["processes"], filter_query)
        
        asyncio.create_task(recreate_records_indexes_from_repositories())
        logging.info(f"Deleted all records and processes for repository {repository_id}")
    except Exception as e:
        logging.error(f"Error deleting records and processes for repository {repository_id}: {e}")
        raise ValueError(f"Error deleting records and processes for repository {repository_id}: {e}")