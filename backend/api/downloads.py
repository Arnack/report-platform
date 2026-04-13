from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import uuid
import os

FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "/app/files")

router = APIRouter(prefix="/api", tags=["downloads"])

# MIME types for different formats
MIME_TYPES = {
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'pdf': 'application/pdf',
    'csv': 'text/csv',
}


@router.get("/runs/{run_id}/download")
async def download_report(run_id: uuid.UUID):
    """Download a generated report file."""
    from models.database import async_session_maker
    from models.report_run import ReportRun
    from sqlalchemy import select
    import asyncio
    
    async with async_session_maker() as session:
        result = await session.execute(select(ReportRun).where(ReportRun.id == run_id))
        run = result.scalar_one_or_none()
        
        if not run:
            raise HTTPException(status_code=404, detail="Report run not found")
        
        if run.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Report is not ready. Current status: {run.status}"
            )
        
        if not run.file_path or not os.path.exists(run.file_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        filename = os.path.basename(run.file_path)
        extension = filename.rsplit('.', 1)[-1] if '.' in filename else 'xlsx'
        media_type = MIME_TYPES.get(extension, 'application/octet-stream')
        
        return FileResponse(
            path=run.file_path,
            filename=filename,
            media_type=media_type,
        )
