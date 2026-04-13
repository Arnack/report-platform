from tasks.celery_app import celery_app
from reports.registry import get_report_generator
from models.database import async_session_maker
from models.report_run import ReportRun
from schemas.report import ReportStatus
from sqlalchemy import update
import os
import uuid
from datetime import datetime

FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "/app/files")


@celery_app.task(bind=True, name="tasks.generate_report")
def generate_report_task(self, run_id: str, report_type: str, params: dict):
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
            
            try:
                # Get report generator
                generator = get_report_generator(report_type)
                
                # Create output path
                os.makedirs(FILE_STORAGE_PATH, exist_ok=True)
                filename = f"{run_id}_{report_type}.xlsx"
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
                
                raise
    
    # Run async code in Celery task
    return asyncio.run(_generate())
