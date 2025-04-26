from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from app.utils.auth_utils import get_current_user
from app.models.repository import Repository
from app.utils.general_utils import get_query_params
from app.utils.repository_utils import process_repository_data
from app.database import db
from bson.objectid import ObjectId
import pandas as pd
from io import BytesIO

router = APIRouter()


async def get_file_parameters(repository: Repository) -> List[dict]:
    """Get parameters from the uploaded CSV file."""
    if repository.file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
    file_content = await repository.file.read()
    csv_data = pd.read_csv(BytesIO(file_content))
    column_names = list(csv_data.columns)
    complete_record = None
    
    for _, row in csv_data.iterrows():
        if row.notnull().all():
            complete_record = row
            break
    
    if complete_record is None:
        raise HTTPException(status_code=400, detail="No complete record found in the CSV file.")
    
    column_info = []
    
    for col in column_names:
        value = complete_record[col]
        if isinstance(value, (int, float)):
            column_type = "number"
        elif isinstance(value, str):
            column_type = "string"
        else:
            column_type = "unknown"
        column_info.append({"name": col, "type": column_type})

    return column_info

async def upsert_repository(repository: Repository, current_user: dict) -> dict:
    """Upsert a repository."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    repository["file_uploaded_at"] = int(time.time())
    
    if repository["_id"] is None:
        if not hasattr(repository, 'file'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
        
        repository["prepared_data"] = False
        repository["type"] = "text/csv"
        parameters = await get_file_parameters(repository)
        repository["parameters"] = parameters
        
        result = await db["repositories"].insert_one(repository)
        repository["_id"] = result.inserted_id
    
    if repository["_id"] is not None:
        if hasattr(repository, 'file')
            repository["prepared_data"] = False
            repository["type"] = "text/csv"
            parameters = await get_file_parameters(repository) 
            await db["records"].delete_many({"repository": repository["_id"]})
    
        result = await db["repositories"].update_one(repository)

    if hasattr(repository, 'file')
        background_tasks = BackgroundTasks()
        background_tasks.add_task(process_repository_data, str(repository["_id"]))
    
    return {"id": str(repository["_id"]), "message": "Repository stored successfully"}


@router.get("/")
async def get_repositories(request:  Request, current_user: dict = Depends(get_current_user)) -> dict:
    """Get all repositories with pagination and filtering."""
    parameters = get_query_params(request)
    repositories = await db["repositories"].find(parameters["query_params"]).skip(parameters["offset"]).limit(parameters["limit"]).to_list(length=None)

    return {"repositories": repositories}

@router.put("/{repository_id}")
async def update_repository(repository: Repository, current_user: dict = Depends(get_current_user)) -> dict:
    """Update a repository by ID."""
    repository["_id"] = ObjectId(repository_id)
    return await upsert_repository(repository, current_user)

@router.post("/")
async def create_repository(repository: Repository, current_user: dict = Depends(get_current_user)) -> dict:
    """Create a new repository."""
    return await upsert_repository(repository, current_user)
