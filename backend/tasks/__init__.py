from tasks.celery_app import celery_app
from tasks.report_tasks import generate_report_task

__all__ = ["celery_app", "generate_report_task"]
