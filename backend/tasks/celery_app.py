from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "report_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max runtime
    task_soft_time_limit=3000,  # 50 minutes soft limit
    # Celery Beat schedule
    beat_schedule={
        "cleanup-old-files": {
            "task": "tasks.cleanup_old_files",
            "schedule": 3600.0,  # Every hour
        },
    },
)
