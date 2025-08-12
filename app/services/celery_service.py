from celery.result import AsyncResult
from app.celery_app import celery_app

def get_task_data(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return result