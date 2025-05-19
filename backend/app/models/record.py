from pydantic import BaseModel
from bson import ObjectId
from typing import Optional, Any

class Record(BaseModel):
    _id: Optional[ObjectId] = None
    repository: ObjectId
    data: dict
    created_at: Optional[Any]
    updated_at: Optional[Any]
    version: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True