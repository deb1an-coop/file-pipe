from celery import Celery
from kombu import Queue
from typing import Optional
import os
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

# Initialize Celery app
celery_app = Celery(
    "fastapi_celery_app",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

# Import tasks to register them
from app.tasks import background_tasks


celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,


    task_track_started=True,
    task_send_sent_event=True,
    task_time_limit = 30 * 60,
    task_soft_time_limit = 25 * 60,

    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1,
    worker_disable_rate_limits=False,

    result_expires=3600,
    result_persistent=True,

    task_routes={
        "app.tasks.background_tasks.process_data_task": {"queue": "data_processing"},
        "app.tasks.background_tasks.process_file_task": {"queue": "file_processing"},
        "app.tasks.background_tasks.send_email_task": {"queue": "emails"},
        "app.tasks.background_tasks.generate_report_task": {"queue": "reports"},
    },

    task_default_queue='default',
    task_queues=(
        Queue("default"),
        Queue("data_processing"),
        Queue("file_processing"),
        Queue("emails"),
        Queue("reports"),
        Queue("high_priority"),
        Queue("low_priority"),
    ),


    task_acks_late=True,
    task_reject_on_worker_lost=True,


    beat_schedule={
        "cleanup-old-tasks": {
            "task": "app.tasks.background_tasks.cleanup_old_tasks",
            "schedule": 3600.0,  # every hour
        },
    },
)


celery_app.conf.task_default_priority = 5
celery_app.conf.worker_hijack_root_logger = False


def create_celery_app() -> Celery:
    """
    Factory function to create and configure the Celery app.
    This allows for dynamic configuration based on environment variables.
    """
    return celery_app


@celery_app.task
def health_check() -> str:
    """
    A simple health check task to verify that the Celery worker is running.
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat(), "message": "Celery worker is running."}

@celery_app.task
def cleanup_old_tasks(days: int = 7) -> None:
    """
    A task to clean up old tasks from the database.
    """
    # TBD: Implement the logic to clean up old tasks
    # This is a placeholder for the actual cleanup logic.
    pass


if __name__ == "__main__":
    celery_app.start()