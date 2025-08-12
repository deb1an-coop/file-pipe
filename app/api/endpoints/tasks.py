import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.celery_app import celery_app
from app.models.task_models import (
    CreateTaskRequest,
    TaskListResponse,
    TaskResponse,
    TaskStatus,
    TaskStatusResponse,
    TaskType,
)
from app.services.celery_service import get_task_data
from app.tasks.background_tasks import (
    generate_report_task,
    process_data_task,
    process_file_task,
    send_email_task,
)

# Assuming you have an authentication dependency
# from app.core.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


def get_task_info(task_id: str) -> TaskResponse:
    """Get task information from Celery"""
    try:
        result = celery_app.AsyncResult(task_id)

        # Get task info with all required fields initialized
        task_info = {
            "task_id": task_id,
            "status": TaskStatus(result.status),
            "created_at": datetime.utcnow(),  # This would come from your DB in real app
            "started_at": datetime.utcnow(),  # Always provide a value for now
            "completed_at": None,
            "progress": 0,
            "result": None,
            "error": None,
            "task_type": TaskType.DATA_PROCESSING,  # Default, should be from DB
            "description": None,
        }

        if result.state == "PENDING":
            task_info.update({"progress": 0, "result": None, "error": None})
        elif result.state == "PROGRESS" or result.state == "STARTED":
            info = result.info or {}
            task_info.update(
                {
                    "progress": info.get("progress", 0),
                    "result": info.get("status"),
                    "started_at": datetime.fromisoformat(info["started_at"])
                    if info.get("started_at")
                    else datetime.utcnow(),
                }
            )
        elif result.state == "SUCCESS":
            task_info.update(
                {
                    "progress": 100,
                    "result": result.result,
                    "completed_at": datetime.utcnow(),  # This would come from result in real app
                    "error": None,
                }
            )
        elif result.state == "FAILURE":
            info = result.info or {}
            task_info.update(
                {
                    "progress": info.get("progress", 0),
                    "result": None,
                    "error": str(result.info) if result.info else "Unknown error",
                    "completed_at": datetime.utcnow(),
                }
            )

        # Debug: Print the task_info to see what we're passing to TaskResponse
        logger.info(f"Task info before TaskResponse creation: {task_info}")

        return TaskResponse(**task_info)

    except Exception as e:
        logger.error(f"Error getting task info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task information")


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    # current_user = Depends(get_current_user)  # Uncomment when auth is ready
):
    """Create a new background task"""
    try:
        task_id = None

        if request.task_type == TaskType.DATA_PROCESSING:
            params = request.parameters
            task = process_data_task.delay(
                params.data_size, params.processing_time, params.include_error
            )
            task_id = task.id

        elif request.task_type == TaskType.FILE_PROCESSING:
            params = request.parameters
            task = process_file_task.delay(params.file_url, params.operation)
            task_id = task.id

        elif request.task_type == TaskType.EMAIL_SENDING:
            params = request.parameters
            task = send_email_task.delay(
                params.recipient, params.subject, params.message, params.delay_seconds
            )
            task_id = task.id

        elif request.task_type == TaskType.REPORT_GENERATION:
            task = generate_report_task.delay(
                request.parameters.get("report_type", "default"), request.parameters
            )
            task_id = task.id

        else:
            raise HTTPException(status_code=400, detail="Invalid task type")

        if not task_id:
            raise HTTPException(status_code=500, detail="Failed to create task")

        # In a real application, you'd save task info to database here
        logger.info(f"Created task {task_id} of type {request.task_type}")

        return get_task_info(task_id)

    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    # current_user = Depends(get_current_user)
):
    """Get the status of a specific task"""
    try:
        task_info = get_task_data(task_id)
        logger.info(f"Retrieved task info: {task_info}")
        return TaskStatusResponse(
            task_id=task_info.task_id,
            status=task_info.status,
            progress=task_info.progress,
            result=task_info.result,
            error=task_info.error,
            created_at=task_info.created_at,
            started_at=task_info.started_at,
            completed_at=task_info.completed_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task status")


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    # current_user = Depends(get_current_user)
):
    """Cancel a running task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f"Task {task_id} cancelled")
        return {"message": f"Task {task_id} has been cancelled"}
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel task")


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[TaskStatus] = None,
    task_type: Optional[TaskType] = None,
    # current_user = Depends(get_current_user)
):
    """List tasks (Note: This is a simplified version - in production you'd store tasks in DB)"""
    # This is a placeholder - in a real app you'd query your database
    # For demo purposes, we'll return empty results
    return TaskListResponse(tasks=[], total=0, page=page, page_size=page_size)


# Helper endpoints for testing
@router.post("/test/data-processing", response_model=TaskResponse)
async def test_data_processing(
    data_size: int = 1000, processing_time: int = 10, include_error: bool = False
):
    """Quick test endpoint for data processing"""
    request = CreateTaskRequest(
        task_type=TaskType.DATA_PROCESSING,
        parameters={
            "data_size": data_size,
            "processing_time": processing_time,
            "include_error": include_error,
        },
        description=f"Test data processing task - {data_size} items",
    )
    return await create_task(request)


@router.post("/test/email", response_model=TaskResponse)
async def test_email_task(
    recipient: str = "test@example.com",
    subject: str = "Test Email",
    message: str = "This is a test email from the task system",
    delay_seconds: int = 0,
):
    """Quick test endpoint for email sending"""
    request = CreateTaskRequest(
        task_type=TaskType.EMAIL_SENDING,
        parameters={
            "recipient": recipient,
            "subject": subject,
            "message": message,
            "delay_seconds": delay_seconds,
        },
        description="Test email task",
    )
    return await create_task(request)
