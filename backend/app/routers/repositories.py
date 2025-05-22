from fastapi import APIRouter, Response, Request, HTTPException, Depends, Form, File, UploadFile
from app.utils.auth_utils import get_current_user
from app.models.repository import Repository
from app.utils.general_utils import get_query_params
from app.utils.repositories_utils import upsert_repository
from app.database import db
from bson.objectid import ObjectId
from bson import json_util

router = APIRouter()


@router.get("/")
async def get_repositories(request:  Request):
    """Get all repositories with pagination and filtering."""
    try:
        parameters = get_query_params(request)
        print('parameters["query_params"]', parameters["query_params"])
        totalItems = await db["repositories"].count_documents(parameters["query_params"])
        page = parameters["page"]
        totalPages = totalItems // parameters["limit"] + (1 if totalItems % parameters["limit"] > 0 else 0)
        repositories = await db["repositories"].find(parameters["query_params"], parameters["select"]).skip(parameters["offset"]).limit(parameters["limit"]).to_list(length=None)

        return Response(status_code=200, content=json_util.dumps({"totalPages": totalPages, "page": page, "items": repositories}), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}")

@router.put("/{repository_id}")
async def update_repository(
    name: str = Form(...),
    description: str = Form(None),
    url: str = Form(...),
    large_file: bool = Form(False),
    file_path: str = Form(""),
    file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
    ) -> dict:
    """Update a repository by ID."""
    
    return await upsert_repository(repository_id, name, description, url, large_file, file_path, file, current_user, "update")

@router.post("/")
async def create_repository(
    name: str = Form(...),
    description: str = Form(None),
    url: str = Form(...),
    large_file: bool = Form(False),
    file_path: str = Form(""),
    file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Create a new repository."""
    
    return await upsert_repository(None, name, description, url, large_file, file_path, file, current_user, "create")

@router.delete("/{repository_id}")
async def delete_repository(repository_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """Delete a repository by ID."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        await db["repositories"].delete_one({"_id": ObjectId(repository_id)})
        await db["records"].delete_many({"repository": ObjectId(repository_id)})
        await db["processes"].delete_many({"repository": ObjectId(repository_id)})

        return {"message": "Repository deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting repository: {str(e)} and all correspinding data")
