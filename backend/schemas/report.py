from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class ReportStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportInfo(BaseModel):
    id: str
    name: str
    description: str
    params_schema: Optional[Dict[str, Any]] = None


class RunReportRequest(BaseModel):
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ReportRunResponse(BaseModel):
    id: UUID
    report_type: str
    status: ReportStatus
    params: Dict[str, Any] = {}
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None


class ReportRunListResponse(BaseModel):
    runs: list[ReportRunResponse]
    total: int
