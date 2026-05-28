from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: str
    source_config: dict = {}
    transform_type: str
    transform_config: dict = {}
    destination_type: str
    destination_config: dict = {}
    schedule_cron: Optional[str] = None


class PipelineOut(BaseModel):
    id: str
    name: str
    source_type: str
    transform_type: str
    destination_type: str
    schedule_cron: Optional[str]
    is_active: bool
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class PipelineRunOut(BaseModel):
    id: str
    pipeline_id: str
    status: str
    trigger: str
    rows_processed: int
    bytes_read: int
    bytes_written: int
    duration_seconds: float
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class QualityCheckOut(BaseModel):
    id: str
    pipeline_id: str
    check_type: str
    column_name: Optional[str]
    threshold: Optional[float]
    actual_value: Optional[float]
    passed: Optional[bool]
    details: Optional[str]
    checked_at: datetime

    class Config:
        from_attributes = True


class LineageNodeOut(BaseModel):
    id: str
    pipeline_id: str
    node_name: str
    node_type: str
    upstream_nodes: list
    downstream_nodes: list
    columns: list

    class Config:
        from_attributes = True
