from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRY = "RETRY"
    REVOKED = "REVOKED"
    PROGRESS = "PROGRESS"


class TaskType(str, Enum):
    DATA_PROCESSING = "data_processing"
    FILE_PROCESSING = "file_processing"
    EMAIL_SENDING = "email_sending"
    REPORT_GENERATION = "report_generation"


class DataProcessingRequest(BaseModel):
    data_size: int = 1000
    processing_time: float = 10.0  # seconds
    include_error: bool = False


class FileProcessingRequest(BaseModel):
    file_url: str
    operation: str = "analyze"


class EmailTaskRequest(BaseModel):
    recipient: str
    subject: str
    message: str
    delay_seconds: int = 0


class ReportGenerationRequest(BaseModel):
    report_type: str = "monthly"
    format: str = "pdf"
    data_range: str = "last_30_days"


class CreateTaskRequest(BaseModel):
    task_type: TaskType
    parameters: Union[
        DataProcessingRequest,
        FileProcessingRequest,
        EmailTaskRequest,
        ReportGenerationRequest,
    ]
    description: Optional[str] = None
    priority: int = Field(default=0, ge=0, le=10)

    class Config:
        schema_extra = {
            "examples": {
                "data_processing": {
                    "task_type": "DATA_PROCESSING",
                    "parameters": {
                        "data_size": 1000,
                        "processing_time": 10,
                        "include_error": False,
                    },
                    "description": "Process 1000 data items",
                    "priority": 1,
                },
                "email_sending": {
                    "task_type": "EMAIL_SENDING",
                    "parameters": {
                        "recipient": "user@example.com",
                        "subject": "Test Email",
                        "message": "This is a test message",
                        "delay_seconds": 0,
                    },
                    "description": "Send notification email",
                    "priority": 2,
                },
            }
        }


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
    progress: Optional[int] = None


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: Optional[int] = None
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
