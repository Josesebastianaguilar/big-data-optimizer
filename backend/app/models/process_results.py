from pydantic import BaseModel
from typing import Optional, Any
from bson import ObjectId

class ProcessResults(BaseModel):
  _id: Optional[ObjectId]
  process_item_id: ObjectId
  process_id: ObjectId
  batch_number: int
  metrics: Optional[Any]
  type: Optional[str]
  input_data_size: Optional[int]
  output_data_size: Optional[int]
  results: Optional[Any]
  errors: Optional[Any]
  created_at: Optional[Any]
  updated_at: Optional[Any]
  
  class Config:
    arbitrary_types_allowed = True