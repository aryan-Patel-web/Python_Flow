"""
Celery Configuration for Background Tasks
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Configure Redis URL
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery instance
celery_app = Celery('ai_social_automation')

# Configure Celery
celery_app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.workers.content_generation_worker.*': {'queue': 'content'},
        'app.workers.auto_posting_worker.*': {'queue': 'posting'},
        'app.workers.analytics_collection_worker.*': {'queue': 'analytics'},
        'app.workers.credential_verification_worker.*': {'queue': 'verification'},
    },
    beat_schedule={
        'auto-post-content': {
            'task': 'app.workers.auto_posting_worker.process_scheduled_posts',
            'schedule': 300.0,  # Every 5 minutes
        },
        'collect-analytics': {
            'task': 'app.workers.analytics_collection_worker.collect_all_analytics',
            'schedule': 3600.0,  # Every hour
        },
        'generate-content': {
            'task': 'app.workers.content_generation_worker.generate_scheduled_content',
            'schedule': 1800.0,  # Every 30 minutes
        },
        'verify-credentials': {
            'task': 'app.workers.credential_verification_worker.verify_all_credentials',
            'schedule': 86400.0,  # Daily
        }
    }
)

# Auto-discover tasks (these will be created when needed)
celery_app.autodiscover_tasks([
    'app.workers.content_generation_worker',
    'app.workers.auto_posting_worker',
    'app.workers.analytics_collection_worker',
    'app.workers.credential_verification_worker',
])

@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'

# Health check task
@celery_app.task
def health_check():
    """Health check for Celery workers"""
    from datetime import datetime
    return {
        'status': 'healthy', 
        'timestamp': datetime.utcnow().isoformat()
    }

if __name__ == '__main__':
    celery_app.start()