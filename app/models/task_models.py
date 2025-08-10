from pydantic import BaseModel
from typing import Optional, Any, Dict
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class TaskType(str, Enum):
    DATA_PROCESSING = "data_processing"
    FILE_PROCESSING = "file_processing"
    EMAIL_SENDING = "email_sending"
    REPORT_GENERATION = "report_generation"


class CreateTaskRequest(BaseModel):
    task_type: TaskType
    parameters: Dict[str, Any]
    description: Optional[str] = None
    priority: Optional[int] = None


class DataProcessingRequest(BaseModel):
    data_size: int = 1000
    processing_time: float = 10.0 # seconds
    include_error: bool = False


class FileProcessingRequest(BaseModel):
    file_url: str
    operation: str = "analyze"


class EmailTaskRequest(BaseModel):
    recipient: str
    subject: str
    message: str
    delay_seconds: int = 0


class TaskResponse(BaseModel):
    task_id: str
    task_type: TaskType
    status: TaskStatus
    description: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: Optional[int] = 0  # Set default value instead of None


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None