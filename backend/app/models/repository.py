from pydantic import BaseModel
from bson import ObjectId
from typing import Optional, List
from fastapi import UploadFile

class Repository(BaseModel):
    _id: Optional[ObjectId] = None
    name: str
    description: str
    url: str
    type: str
    prepared_data: Optional[bool] = None
    file: Optional[UploadFile] = None
    file_uploaded_at: Optional[int] = None
    data_updated_at: Optional[int] = None
    parameters: Optional[List[dict]] = None
    
    