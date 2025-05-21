from pydantic import BaseModel
from bson import ObjectId
from typing import Optional, Any

class User(BaseModel):
    _id: Optional[Any] = None
    username: str
    role: Optional[str] = "user"
    password: str

class Token(BaseModel):
    _id: Optional[str]
    access_token: str
    token_type: str
    username: Optional[str]
    role: Optional[str]