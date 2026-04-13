from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import List
import uuid
from datetime import datetime, timedelta

from models.database import get_db
from models.report_run import ReportRun
from schemas.report import (
    ReportInfo,
    RunReportRequest,
    ReportRunResponse,
    ReportRunListResponse,
    ReportStatus,
)
from reports.registry import get_all_reports, get_report_generator, get_available_formats
from tasks.report_tasks import generate_report_task

router = APIRouter(prefix="/api", tags=["reports"])


@router.get("/reports", response_model=List[ReportInfo])
async def list_available_reports():
    """List all available report types."""
    reports = get_all_reports()
    result = []
    for r in reports:
        formats = get_available_formats(r.id)
        info = ReportInfo(
            id=r.id,
            name=r.name,
            description=r.description,
            params_schema=r.params_schema,
            available_formats=formats,
        )
        result.append(info)
    return result


@router.post("/reports/{report_id}/run", response_model=ReportRunResponse, status_code=202)
async def run_report(
    report_id: str,
    request: RunReportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Trigger report generation (async)."""
    # Validate report type
    try:
        output_format = request.output_format or "xlsx"
        generator = get_report_generator(report_id, output_format)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    params = request.params or {}
    cache_ttl = request.cache_ttl_seconds or 0
    
    # Check cache: look for completed run with same params within TTL
    if cache_ttl > 0:
        cutoff_time = datetime.utcnow() - timedelta(seconds=cache_ttl)
        cache_query = select(ReportRun).where(
            and_(
                ReportRun.report_type == report_id,
                ReportRun.status == ReportStatus.COMPLETED.value,
                ReportRun.created_at >= cutoff_time,
                ReportRun.params == params,
            )
        ).order_by(desc(ReportRun.created_at)).limit(1)
        
        result = await db.execute(cache_query)
        cached_run = result.scalar_one_or_none()
        
        if cached_run:
            # Return cached result
            return ReportRunResponse(
                id=cached_run.id,
                report_type=cached_run.report_type,
                status=ReportStatus(cached_run.status),
                params=cached_run.params,
                created_at=cached_run.created_at,
                completed_at=cached_run.completed_at,
                file_path=cached_run.file_path,
                error_message=cached_run.error_message,
                cached=True,
            )
    
    # Create new run record
    run = ReportRun(
        report_type=report_id,
        status=ReportStatus.PENDING.value,
        params=params,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Queue Celery task
    generate_report_task.delay(
        run_id=str(run.id),
        report_type=report_id,
        params=params,
        output_format=output_format,
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
        cached=False,
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
