"""
Celery configuration for Church Directory marketing site.
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verionlabs_django.settings')

app = Celery('church_directory')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Explicitly import tasks to ensure they're registered
app.autodiscover_tasks(['church_directory'])

# Celery configuration
app.conf.update(
    # Task routing - Use default queue for now to avoid routing issues
    # task_routes={
    #     'church_directory.tasks.create_backend_organization_task': {'queue': 'backend_integration'},
    #     'church_directory.tasks.retry_failed_backend_integrations': {'queue': 'maintenance'},
    #     'church_directory.tasks.health_check_backend_integrations': {'queue': 'monitoring'},
    # },
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Prevent workers from hogging tasks
    task_acks_late=True,          # Acknowledge tasks only after completion
    
    # Retry settings
    task_retry_jitter=True,       # Add randomness to retry delays
    task_default_retry_delay=60,  # Default retry delay (1 minute)
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'retry-failed-integrations': {
            'task': 'church_directory.tasks.retry_failed_backend_integrations',
            'schedule': 3600.0,  # Run every hour
        },
        'backend-integration-health-check': {
            'task': 'church_directory.tasks.health_check_backend_integrations', 
            'schedule': 1800.0,  # Run every 30 minutes
        },
    },
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')