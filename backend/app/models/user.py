from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class User(BaseModel):
    _id: Optional[ObjectId] = None
    username: str
    role: Optional[str] = "user"
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str