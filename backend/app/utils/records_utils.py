from fastapi import HTTPException
from app.database import db
from datetime import datetime
from typing import Any, List
from dotenv import load_dotenv
from io import BytesIO
from app.models.repository import Repository
from pathlib import Path
from bson.objectid import ObjectId
from app.database import recreate_records_indexes_from_repositories
import mimetypes
import pandas as pd
import logging
import os
import chardet

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
RECORDS_BATCH_SIZE = int(os.getenv("RECORDS_BATCH_SIZE", "5000"))  # Default to 5000 records per batch


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

async def delete_repository_related_data(repository_id: str, reset_indexes: bool = True):
    """
    Delete all records and processes related to the repository.
    """
    try:
        logging.info(f"Deleting all records and processes for repository {repository_id}")
        filter_query = {"repository": ObjectId(repository_id)}
        await delete_collection_in_batches(db["records"], filter_query)
        await delete_collection_in_batches(db["processes"], filter_query)
        if reset_indexes is True:
            await recreate_records_indexes_from_repositories()
        
        logging.info(f"Deleted all records and processes for repository {repository_id}")
    except Exception as e:
        logging.error(f"Error deleting records and processes for repository {repository_id}: {e}")
        raise ValueError(f"Error deleting records and processes for repository {repository_id}: {e}")

async def store_repository_records(repository: Repository, delete_existing_records: bool = False):
    try:
        # Delete existing records if needed
        if delete_existing_records:
            try:
                await delete_repository_related_data(str(repository["_id"]), False)
            except Exception as e:
                logging.error(f"Error deleting existing records and processes for repository {repository['_id']}: {e}")
                raise ValueError(f"Error deleting existing records and processes for repository {repository['_id']}: {e}")

        # Determine file source
        file_path = None
        file_content = None
        if "file" in repository and repository["file"] is not None:
            logging.info("Processing file from repository object")
            file_content = repository["file"]
            file_size = len(file_content) / (1024 * 1024)
            file_stream = BytesIO(file_content)
        elif repository.get("large_file") and repository.get("file_path"):
            logging.info("Processing large file from file_path")
            file_path = os.path.join(UPLOAD_DIR, repository["file_path"])
            if not os.path.exists(file_path):
                logging.error(f"File {file_path} does not exist.")
                raise ValueError(f"File {file_path} does not exist.")
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            file_stream = file_path  # pandas can take a file path
        else:
            logging.error("No file or file_path provided for processing.")
            raise ValueError("No file or file_path provided for processing.")

        now = datetime.now()
        batch_size = RECORDS_BATCH_SIZE
        total_inserted = 0
        parameters = []
        column_names = []
        found_complete_row = None

        # Read in chunks
        logging.info(f"Processing file: {UPLOAD_DIR}/{repository['file_path']}")
        logging.info(f"Reading CSV file in chunks of {batch_size} rows")
        
        def detect_encoding(file_path, sample_size=10000):
            with open(file_path, 'rb') as f:
                rawdata = f.read(sample_size)
            result = chardet.detect(rawdata)
            return result['encoding'] or 'utf-8'
        
        encoding = detect_encoding(file_path)
        logging.info(f"Detected encoding: {encoding}")
        
        for i, chunk in enumerate(pd.read_csv(file_stream, chunksize=batch_size, encoding=encoding, on_bad_lines="warn")):
            chunk = chunk.where(pd.notnull(chunk), None)
            if i == 0:
                # Infer columns and types from the first non-empty chunk
                column_names = list(chunk.columns)
                # Find a row with no nulls to infer types
                for _, row in chunk.iterrows():
                    if row.notnull().all():
                        found_complete_row = row
                        break
                if found_complete_row is None and not chunk.empty:
                    found_complete_row = chunk.loc[chunk.isnull().sum(axis=1).idxmin()]
                if found_complete_row is None:
                    logging.error("The CSV file is empty or contains no valid records.")
                    raise ValueError("The CSV file is empty or contains no valid records.")
                # Infer parameter types
                parameters = []
                for col in column_names:
                    value = found_complete_row[col]
                    if isinstance(value, (int, float)):
                        column_type = "number"
                    elif isinstance(value, str):
                        column_type = "string"
                    else:
                        column_type = "string"
                    parameters.append({"name": col, "type": column_type})

            records_data = chunk.to_dict(orient="records")
            records = [
                {
                    "repository": ObjectId(repository['_id']),
                    "data": record,
                    "created_at": now,
                    "updated_at": now,
                    "version": 0
                }
                for record in records_data
            ]
            if records:
                await db["records"].insert_many(records)
                total_inserted += len(records)
        
        # Update repository info
        repository_data = {
            "data_ready": True,
            "valid": True,
            "file_size": file_size,
            "type": "text/csv",
            "original_data_size": total_inserted,
            "current_data_size": total_inserted,
            "data_updated_at": datetime.now(),
            "parameters": parameters,
        }
        await db["repositories"].update_one({"_id": ObjectId(repository['_id'])}, {"$set": repository_data})
        logging.info(f"Inserted total {total_inserted} records for repository {repository['_id']}")

        # Optionally delete the file after processing
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"Deleted file at {file_path}")
            except Exception as e:
                logging.error(f"Error deleting file at {file_path}: {e}")

        await recreate_records_indexes_from_repositories()

    except Exception as e:
        logging.error(f"Error storing records for repository {repository['_id']}: {e}", exc_info=True)
        raise ValueError(f"Error storing records for repository {repository['_id']}: {e}")
