from pydantic import BaseModel
from bson import ObjectId
from typing import Optional

class Record(BaseModel):
    _id: Optional[ObjectId] = None
    repository: ObjectId
    data: dict
    created_at : int = None
    