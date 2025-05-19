from fastapi import APIRouter, Response, Request, HTTPException, Depends
from app.utils.auth_utils import get_current_user
from app.models.repository import Repository
from app.utils.general_utils import get_query_params
from app.utils.repositories_utils import upsert_repository
from app.database import db
from bson.objectid import ObjectId

router = APIRouter()


@router.get("/")
async def get_repositories(request:  Request, current_user: dict = Depends(get_current_user)) -> dict:
    """Get all repositories with pagination and filtering."""
    try:
        parameters = get_query_params(request)
        repositories = await db["repositories"].find(parameters["query_params"]).skip(parameters["offset"]).limit(parameters["limit"]).to_list(length=None)

        return Response(status_code=200, content={"repositories": repositories})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}")

@router.put("/{repository_id}")
async def update_repository(repository: Repository, current_user: dict = Depends(get_current_user)) -> dict:
    """Update a repository by ID."""
    repository["_id"] = ObjectId(repository_id)
    return await upsert_repository(repository, current_user)

@router.post("/")
async def create_repository(repository: Repository, current_user: dict = Depends(get_current_user)) -> dict:
    """Create a new repository."""
    return await upsert_repository(repository, current_user)

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
