from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth_utils import create_access_token, get_current_user, get_user, verify_password, hash_password
from app.models.user import User, Token
from app.database import db
from datetime import timedelta
from bson.objectid import ObjectId

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user: User):
    """
    Login a user and return an access token.
    """
    try:
        db_user = await get_user(user.username)
        
        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
        
        return {"access_token": access_token, "token_type": "bearer", "user": db_user.copy().pop("password")}
    except Exception as e:
        raise e

@router.post("/register")
async def register(user: User):
    """
    Register a new user. If there are already 2 users, the new user will be an admin.
    """
    try:
        existing_users = await db["users"].find({}, {"_id": 1, "username": 1, "role": 1}).to_list(length=None)
        
        if len(existing_users) >= 2:
            raise HTTPException(status_code=400, detail="Users max number already reached")
        
        
        if any(existing_user["username"] == user.username for existing_user in existing_users):
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = hash_password(user.password)
        role_name = "user"
        
        for existing_user in existing_users:
            if existing_user["role"] == "user":
                role_name = role_name = "admin"
        
        new_user = {"username": user.username, "role": role_name, "password": hashed_password}
        result = await db["users"].insert_one(new_user)
        
        return {"id": str(result.inserted_id), "username": user.username}
    except Exception as e: 
        raise e
