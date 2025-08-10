import time
import random
from datetime import datetime
from typing import Dict, Any
from celery import Celery
from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_data_task(self, data_size: int, processing_time: int, include_error: bool = False):
    """
    Simulate data processing task with progress updates
    """
    try:
        # Update task state to STARTED
        self.update_state(
            state='STARTED',
            meta={
                'progress': 0,
                'status': 'Processing started',
                'started_at': datetime.utcnow().isoformat()
            }
        )
        
        # Simulate processing with progress updates
        total_steps = 10
        for i in range(total_steps):
            if include_error and i == 7:  # Simulate error at 70%
                raise Exception("Simulated processing error")
                
            # Simulate work
            time.sleep(processing_time / total_steps)
            
            progress = int((i + 1) / total_steps * 100)
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'status': f'Processing step {i + 1}/{total_steps}',
                    'current_step': i + 1,
                    'total_steps': total_steps
                }
            )
        
        # Generate mock results
        result = {
            'data_processed': data_size,
            'processing_time': processing_time,
            'records_created': random.randint(100, 1000),
            'records_updated': random.randint(50, 500),
            'completed_at': datetime.utcnow().isoformat(),
            'summary': f'Successfully processed {data_size} data items'
        }
        
        return {
            'progress': 100,
            'status': 'Processing completed successfully',
            'result': result
        }
        
    except Exception as exc:
        logger.error(f"Data processing task failed: {exc}")
        self.update_state(
            state='FAILURE',
            meta={
                'error': str(exc),
                'progress': self.request.kwargs.get('progress', 0),
                'failed_at': datetime.utcnow().isoformat()
            }
        )
        raise


@celery_app.task(bind=True)
def process_file_task(self, file_url: str, operation: str = "analyze"):
    """
    Simulate file processing task
    """
    try:
        self.update_state(
            state='STARTED',
            meta={
                'progress': 0,
                'status': 'File processing started',
                'file_url': file_url,
                'operation': operation
            }
        )
        
        # Simulate file download
        time.sleep(2)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 25, 'status': 'File downloaded'}
        )
        
        # Simulate file processing
        time.sleep(3)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 75, 'status': f'Performing {operation}'}
        )
        
        # Simulate completion
        time.sleep(1)
        
        result = {
            'file_url': file_url,
            'operation': operation,
            'file_size': random.randint(1000, 10000),
            'processed_at': datetime.utcnow().isoformat(),
            'output_url': f"/processed/{random.randint(1000, 9999)}.json"
        }
        
        return {
            'progress': 100,
            'status': 'File processing completed',
            'result': result
        }
        
    except Exception as exc:
        logger.error(f"File processing task failed: {exc}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc)}
        )
        raise


@celery_app.task(bind=True)
def send_email_task(self, recipient: str, subject: str, message: str, delay_seconds: int = 0):
    """
    Simulate email sending task
    """
    try:
        if delay_seconds > 0:
            logger.info(f"Delaying email task for {delay_seconds} seconds")
            time.sleep(delay_seconds)
        
        self.update_state(
            state='STARTED',
            meta={
                'progress': 0,
                'status': 'Preparing email',
                'recipient': recipient
            }
        )
        
        # Simulate email preparation
        time.sleep(1)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 50, 'status': 'Sending email'}
        )
        
        # Simulate email sending
        time.sleep(2)
        
        result = {
            'recipient': recipient,
            'subject': subject,
            'message_length': len(message),
            'sent_at': datetime.utcnow().isoformat(),
            'message_id': f"msg_{random.randint(10000, 99999)}"
        }
        
        return {
            'progress': 100,
            'status': 'Email sent successfully',
            'result': result
        }
        
    except Exception as exc:
        logger.error(f"Email task failed: {exc}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc)}
        )
        raise


@celery_app.task(bind=True)
def generate_report_task(self, report_type: str, parameters: Dict[str, Any]):
    """
    Simulate report generation task
    """
    try:
        self.update_state(
            state='STARTED',
            meta={
                'progress': 0,
                'status': 'Report generation started',
                'report_type': report_type
            }
        )
        
        # Simulate data collection
        time.sleep(3)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'status': 'Collecting data'}
        )
        
        # Simulate data processing
        time.sleep(4)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 70, 'status': 'Processing data'}
        )
        
        # Simulate report generation
        time.sleep(2)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 90, 'status': 'Generating report'}
        )
        
        time.sleep(1)
        
        result = {
            'report_type': report_type,
            'parameters': parameters,
            'generated_at': datetime.utcnow().isoformat(),
            'report_url': f"/reports/{random.randint(1000, 9999)}.pdf",
            'page_count': random.randint(5, 50),
            'data_points': random.randint(100, 1000)
        }
        
        return {
            'progress': 100,
            'status': 'Report generated successfully',
            'result': result
        }
        
    except Exception as exc:
        logger.error(f"Report generation task failed: {exc}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(exc)}
        )
        raise