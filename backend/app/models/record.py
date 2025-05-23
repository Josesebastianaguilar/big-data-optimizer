from pydantic import BaseModel
from bson import ObjectId
from typing import Optional, Any, Union, Dict

class Record(BaseModel):
    _id: Optional[Union[ObjectId, str]] = None
    repository: Union[ObjectId, str]
    data: Dict
    created_at: Optional[Any]
    updated_at: Optional[Any]
    version: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True