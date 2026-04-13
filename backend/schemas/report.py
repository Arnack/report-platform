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
    available_formats: list[str] = ["xlsx", "pdf"]


class RunReportRequest(BaseModel):
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    cache_ttl_seconds: Optional[int] = Field(default=3600, ge=0, le=86400)  # Default 1 hour, max 24 hours
    output_format: Optional[str] = Field(default="xlsx", pattern="^(xlsx|pdf)$")  # Output format


class ReportRunResponse(BaseModel):
    id: UUID
    report_type: str
    status: ReportStatus
    params: Dict[str, Any] = {}
    created_at: datetime
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    cached: bool = False


class ReportRunListResponse(BaseModel):
    runs: list[ReportRunResponse]
    total: int
