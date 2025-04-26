from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
from bson import ObjectId
from enum import Enum

class ProcessName(str, Enum):
  FILTER = "filter"
  GROUP = "group"
  AGGREGATION = "aggregation"

class ProcessingType(str, Enum):
  ISOLATED = "isolated"
  SEQUENTIAL = "sequential"

class ProcessingStatus(str, Enum):
  IN_PROGRESS = "in_progress"
  COMPLETED = "completed"
  FAILED = "failed"

class ProcessingMetrics(BaseModel):
  id: Optional[str]
  task_process: ProcessName
  status: ProcessingStatus
  repository: ObjectId
  process_id: ObjectId
  optimized: bool
  external: bool = False
  parameters: List[Union[dict, str]]
  process_type: ProcessingType
  start_time: Optional[datetime]
  end_time: Optional[datetime]
  duration: Optional[datetime]
  input_data_size: Optional[int]
  output_data_size: Optional[int]
  metrics: Optional[dict]
  results: Optional[List[dict]]
  error_message: Optional[str]
  created_at: datetime
  updated_at: datetime