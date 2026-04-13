from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List
import uuid
from datetime import datetime

from models.database import get_db
from models.report_run import ReportRun
from schemas.report import (
    ReportInfo,
    RunReportRequest,
    ReportRunResponse,
    ReportRunListResponse,
    ReportStatus,
)
from reports.registry import get_all_reports, get_report_generator
from tasks.report_tasks import generate_report_task

router = APIRouter(prefix="/api", tags=["reports"])


@router.get("/reports", response_model=List[ReportInfo])
async def list_available_reports():
    """List all available report types."""
    reports = get_all_reports()
    return [
        ReportInfo(
            id=r.id,
            name=r.name,
            description=r.description,
            params_schema=r.params_schema,
        )
        for r in reports
    ]


@router.post("/reports/{report_id}/run", response_model=ReportRunResponse, status_code=202)
async def run_report(
    report_id: str,
    request: RunReportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Trigger report generation (async)."""
    # Validate report type
    try:
        generator = get_report_generator(report_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Create run record
    run = ReportRun(
        report_type=report_id,
        status=ReportStatus.PENDING.value,
        params=request.params or {},
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Queue Celery task
    generate_report_task.delay(
        run_id=str(run.id),
        report_type=report_id,
        params=request.params or {},
    )
    
    return ReportRunResponse(
        id=run.id,
        report_type=run.report_type,
        status=ReportStatus(run.status),
        params=run.params,
        created_at=run.created_at,
        completed_at=run.completed_at,
        file_path=run.file_path,
        error_message=run.error_message,
    )


@router.get("/runs", response_model=ReportRunListResponse)
async def list_report_runs(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all report runs with pagination."""
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(ReportRun))
    total = count_result.scalar()
    
    # Get runs
    result = await db.execute(
        select(ReportRun)
        .order_by(desc(ReportRun.created_at))
        .limit(limit)
        .offset(offset)
    )
    runs = result.scalars().all()
    
    return ReportRunListResponse(
        total=total,
        runs=[
            ReportRunResponse(
                id=run.id,
                report_type=run.report_type,
                status=ReportStatus(run.status),
                params=run.params,
                created_at=run.created_at,
                completed_at=run.completed_at,
                file_path=run.file_path,
                error_message=run.error_message,
            )
            for run in runs
        ],
    )


@router.get("/runs/{run_id}", response_model=ReportRunResponse)
async def get_report_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get status of a specific report run."""
    result = await db.execute(select(ReportRun).where(ReportRun.id == run_id))
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Report run not found")
    
    return ReportRunResponse(
        id=run.id,
        report_type=run.report_type,
        status=ReportStatus(run.status),
        params=run.params,
        created_at=run.created_at,
        completed_at=run.completed_at,
        file_path=run.file_path,
        error_message=run.error_message,
    )
