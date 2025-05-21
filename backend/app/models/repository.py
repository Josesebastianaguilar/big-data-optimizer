from pydantic import BaseModel
from bson import ObjectId
from typing import Optional, List, Any
from fastapi import UploadFile

class Repository(BaseModel):
    _id: Optional[ObjectId] = None
    name: str
    description: Optional[str] = None
    url: str
    type: Optional[str]
    file_path: Optional[str] = None
    data_ready: Optional[bool] = None
    file: Optional[UploadFile] = None
    large_file: Optional[bool] = False
    valid: Optional[bool] = None
    file_size: Optional[Any] = None
    original_data_size: Optional[int] = None
    current_data_size: Optional[int] = None
    data_created_at: Optional[Any] = None
    data_updated_at: Optional[Any] = None
    parameters: Optional[List[dict]] = []
    version: Optional[Any] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    