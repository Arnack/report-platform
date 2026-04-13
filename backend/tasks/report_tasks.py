from tasks.celery_app import celery_app
from reports.registry import get_report_generator
from models.database import async_session_maker
from models.report_run import ReportRun
from schemas.report import ReportStatus
from sqlalchemy import update, select, delete
import os
import uuid
from datetime import datetime, timedelta
import logging
import redis
import json

logger = logging.getLogger(__name__)

FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "/app/files")
FILE_TTL_HOURS = int(os.getenv("FILE_TTL_HOURS", "168"))  # Default 7 days
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def publish_status_update(run_id: str, status: str, **kwargs):
    """Publish status update to Redis Pub/Sub for SSE streaming."""
    try:
        redis_client = redis.from_url(REDIS_URL)
        channel = f"report_status:{run_id}"
        message = {"run_id": run_id, "status": status, **kwargs}
        redis_client.publish(channel, json.dumps(message))
        redis_client.close()
    except Exception as e:
        logger.error(f"Failed to publish status update: {e}")


@celery_app.task(bind=True, name="tasks.generate_report")
def generate_report_task(self, run_id: str, report_type: str, params: dict, output_format: str = "xlsx"):
    """Celery task to generate a report asynchronously."""
    import asyncio
    
    async def _generate():
        async with async_session_maker() as session:
            # Update status to running
            await session.execute(
                update(ReportRun)
                .where(ReportRun.id == uuid.UUID(run_id))
                .values(status=ReportStatus.RUNNING.value)
            )
            await session.commit()
            
            # Publish status update
            publish_status_update(run_id, "running")

            try:
                # Get report generator
                generator = get_report_generator(report_type, output_format)

                # Create output path
                os.makedirs(FILE_STORAGE_PATH, exist_ok=True)
                extension = output_format if output_format != "xlsx" else "xlsx"
                filename = f"{run_id}_{report_type}.{extension}"
                output_path = os.path.join(FILE_STORAGE_PATH, filename)

                # Generate report
                await generator.generate(params, output_path)

                # Update status to completed
                await session.execute(
                    update(ReportRun)
                    .where(ReportRun.id == uuid.UUID(run_id))
                    .values(
                        status=ReportStatus.COMPLETED.value,
                        completed_at=datetime.utcnow(),
                        file_path=output_path
                    )
                )
                await session.commit()
                
                # Publish status update
                publish_status_update(run_id, "completed", file_path=output_path)

                return {"status": "completed", "file_path": output_path}

            except Exception as e:
                # Update status to failed
                await session.execute(
                    update(ReportRun)
                    .where(ReportRun.id == uuid.UUID(run_id))
                    .values(
                        status=ReportStatus.FAILED.value,
                        error_message=str(e),
                        completed_at=datetime.utcnow()
                    )
                )
                await session.commit()
                
                # Publish status update
                publish_status_update(run_id, "failed", error_message=str(e))

                raise
    
    # Run async code in Celery task
    return asyncio.run(_generate())


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files():
    """Celery periodic task to clean up old report files and database records."""
    import asyncio
    
    async def _cleanup():
        cutoff_time = datetime.utcnow() - timedelta(hours=FILE_TTL_HOURS)
        deleted_count = 0
        
        async with async_session_maker() as session:
            # Find old completed runs
            result = await session.execute(
                select(ReportRun).where(
                    ReportRun.status == ReportStatus.COMPLETED.value,
                    ReportRun.completed_at < cutoff_time,
                )
            )
            old_runs = result.scalars().all()
            
            for run in old_runs:
                # Delete file if exists
                if run.file_path and os.path.exists(run.file_path):
                    try:
                        os.remove(run.file_path)
                        logger.info(f"Deleted file: {run.file_path}")
                    except OSError as e:
                        logger.error(f"Failed to delete file {run.file_path}: {e}")
                
                # Delete database record
                await session.delete(run)
                deleted_count += 1
            
            await session.commit()
            
            logger.info(f"Cleanup completed: deleted {deleted_count} old report runs")
            return {"deleted_count": deleted_count}
    
    return asyncio.run(_cleanup())
