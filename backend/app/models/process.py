from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class ProcessName(str, Enum):
  filter = "filter"
  group = "group"
  aggregation = "aggregation"

class Trigger(str, Enum):
  USER = "user"
  SYSTEM = "system"

class ProcessingStatus(str, Enum):
  IN_PROGRESS = "in_progress"
  COMPLETED = "completed"
  FAILED = "failed"

class Process(BaseModel):
  _id: Optional[ObjectId]
  task_process: str
  actions: List[str]
  status: str
  repository: ObjectId
  process_id: ObjectId
  optimized: bool
  parameters: List[Any]
  trigger_type: str
  start_time: Optional[Any]
  end_time: Optional[Any]
  duration: Optional[Any]
  input_data_size: Optional[int]
  output_data_size: Optional[int]
  metrics: Optional[Any]
  results: Optional[Any]
  errors: Optional[Any]
  validated: Optional[bool] = False
  valid: Optional[bool]
  created_at: Optional[Any]
  updated_at: Optional[Any]
  iteration: Optional[int]
  repository_version: Optional[int]
  
  class Config:
    arbitrary_types_allowed = True