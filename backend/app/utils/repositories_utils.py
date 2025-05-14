from fastapi import Request, Response, HTTPException
from typing import List, Any
from app.database import db
from app.models.repository import Repository
from pathlib import Path
from bson.objectid import ObjectId
from fastapi import UploadFile
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import mimetypes
import logging
import os
import asyncio

load_dotenv()
logging.basicConfig(filename=os.getenv("ERROR_LOG_PATH", "error.log"), level=logging.ERROR)

async def store_repository_records(repository: Repository, parameters: List[dict], csv_data: pd.DataFrame, file_size: float, delete_existing_records: bool = False):
    if delete_existing_records:
        try:
            await db["records"].delete_many({"repository": ObjectId(repository['_id'])})
        except Exception as e:
            logging.error(f"Error deleting existing records for repository {repository['_id']}: {e}")
            raise ValueError(f"Error deleting existing records for repository {repository['_id']}: {e}")
    try:
        now = datetime.now()
        records_data = csv_data.to_dict(orient="records")
        records = [{"repository": ObjectId(repository['_id']), "data": record, "created_at": now, "updated_at": now, version: 0} for record in records_data]
        num_records = len(records)
        
        await db["records"].insert_many(records)
        logging.info(f"Inserted {num_records} records for repository {repository['_id']}")

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
        #q: I need to delete the file from the system at repository.file_path
        if repository.large_file and repository.file_path:
            path = Path(repository.file_path)
            if path.exists():
                try:
                    path.unlink()
                    logging.info(f"Deleted file at {repository.file_path}")
                except Exception as e:
                    logging.error(f"Error deleting file at {repository.file_path}: {e}")
                    raise ValueError(f"Error deleting file at {repository.file_path}: {e}")
            else:
                logging.warning(f"File at {repository.file_path} does not exist")
        

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


async def process_file(repository: Repository, delete_existing_records: bool = False) -> List[dict]:
    """Get parameters from the uploaded CSV file."""
    if hasattr(repository, 'file'):
        file_content = await repository.file.read()
    elif repository.large_file is True and repository.file_path:
        file_content = read_file_from_path(repository.file_path)
    
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

def validate_repository_file(repository: Repository):
    if not hasattr(repository, 'file') and repository.large_file is True and repository.file_path is None:
            raise HTTPException(status_code=400, detail="Must specify file_path for large files.")
            
    if hasattr(repository, 'file') and repository.file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
    if not hasattr(repository, 'file') and repository.large_file is True:
        file_path = Path(repository.file_path)

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=400, detail="File does not exist or is not a file.")

        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type != "text/csv":
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")

async def upsert_repository(repository: Repository, current_user: dict) -> dict:
    """Upsert a repository."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if repository["_id"] is None:
        if not hasattr(repository, 'file') and repository.large_file is not True:
            raise HTTPException(status_code=400, detail="File is required for new repositories.")
        
        validate_repository_file(repository)
        now = datetime.now()
        repository_data = {"name": repository.name, "description": repository.description, "url": repository.url, "version": 0, "data_ready": False, "valid": False, "created_at": now, "updated_at": now}

        try:
            result = await db["repositories"].insert_one(repository)
            repository["_id"] = result.inserted_id
            asyncio.create_task(process_file, repository)

            return Response(status_code=201, content={"id": str(repository["_id"]), "message": "Repository created successfully"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error insertincreatingg repository: {str(e)}")
    
    if repository["_id"] is not None:
        validate_repository_file(repository)
        now = datetime.now()
        repository_data = {"name": repository.name, "description": repository.description, "url": repository.url, "version": 0, "updated_at": now}
        if hasattr(repository, 'file') or repository.large_file is True:
            repository_data["data_ready"] = False
            repository_data["valid"] = False
            repository_data["file_size"] = None
            repository_data["original_data_size"] = None
            repository_data["current_data_size"] = None
            repository_data["data_updated_at"] = None

        try:
            result = await db["repositories"].update_one({"_id": repository["_id"]}, {"$set": repository_data})
            
            if hasattr(repository, 'file') or repository.large_file is True:
                asyncio.create_task(process_file, repository, True)
            
            return Response(status_code=200, content={"id": str(repository["_id"]), "message": "Repository updated successfully"})

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating repository: {str(e)}")
        
async def get_repository(repository_id: str) -> dict:
    """
    Validate if the repository exists and is not processed.
    """
    repository = await db["repositories"].find_one({"_id": ObjectId(repository_id)})
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.get("data_ready") is not True:
        raise HTTPException(status_code=500, detail="Data has been not prepared yet")
    
    return repository