from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from app.auth.auth_utils import create_access_token
from app.models.user import User, Token
from app.database import db
from datetime import timedelta
from bson.objectid import ObjectId

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(username: str):
    user = await db["users"].find_one({"username": username})
    return user

@router.post("/login", response_model=Token)
async def login(user: User):
    db_user = await get_user(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(user: User):
    # Fetch only the "username" field for all users
    existing_users = await db["users"].find({}, {"_id": 1, "username": 1}).to_list(length=None)
    
    # Check if the maximum number of users is reached
    if len(existing_users) >= 2:
        raise HTTPException(status_code=400, detail="Users max number already reached")
    
    # Check if the username already exists
    if any(existing_user["username"] == user.username for existing_user in existing_users):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = hash_password(user.password)
    new_user = {"username": user.username, "hashed_password": hashed_password}
    result = await db["users"].insert_one(new_user)
    return {"id": str(result.inserted_id), "username": user.username}