from fastapi import HTTPException
from app.database import db
from datetime import datetime
from typing import Any, List
from dotenv import load_dotenv
from io import BytesIO
from app.models.repository import Repository
from pathlib import Path
from bson.objectid import ObjectId
import mimetypes
from app.database import recreate_records_indexes_from_repositories
import pandas as pd
import logging
import os

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


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
        path = Path(f"{UPLOAD_DIR}/{repository['file_path']}")
        if path.exists():
            try:
                path.unlink()
                logging.info(f"Deleted file at {UPLOAD_DIR}/{repository['file_path']}")
            except Exception as e:
                logging.error(f"Error deleting file at {repository['file_path']}: {e}")
                raise ValueError(f"Error deleting file at {repository['file_path']}: {e}")
        else:
            logging.warning(f"File at {repository['file_path']} does not exist")
        
        await recreate_records_indexes_from_repositories()
        

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
    elif repository["large_file"] is True and repository["file_path"] is not None:
        logging.info(f"Processing large file from path: {UPLOAD_DIR}/{repository['file_path']}")
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
    
async def delete_collection_in_batches(collection, filter_query, batch_size=10000):
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
        await recreate_records_indexes_from_repositories()
        
        logging.info(f"Deleted all records and processes for repository {repository_id}")
    except Exception as e:
        logging.error(f"Error deleting records and processes for repository {repository_id}: {e}")
        raise ValueError(f"Error deleting records and processes for repository {repository_id}: {e}")