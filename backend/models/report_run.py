from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from models.database import Base


class ReportRun(Base):
    __tablename__ = "report_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    params = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    file_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
