import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Text, Integer, Boolean, JSON, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  # S3, POSTGRESQL, KAFKA, API
    source_config: Mapped[dict] = mapped_column(JSON, default=dict)
    transform_type: Mapped[str] = mapped_column(String, nullable=False)  # SPARK_SQL, DBT, PYTHON_UDF
    transform_config: Mapped[dict] = mapped_column(JSON, default=dict)
    destination_type: Mapped[str] = mapped_column(String, nullable=False)  # S3, POSTGRESQL, KAFKA
    destination_config: Mapped[dict] = mapped_column(JSON, default=dict)
    schedule_cron: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    runs: Mapped[list["PipelineRun"]] = relationship("PipelineRun", back_populates="pipeline")
    quality_checks: Mapped[list["QualityCheck"]] = relationship("QualityCheck", back_populates="pipeline")
    lineage_nodes: Mapped[list["LineageNode"]] = relationship("LineageNode", back_populates="pipeline")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id: Mapped[str] = mapped_column(String, ForeignKey("pipelines.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, default="PENDING")  # PENDING, RUNNING, SUCCESS, FAILED
    trigger: Mapped[str] = mapped_column(String, default="MANUAL")  # MANUAL, SCHEDULED
    rows_processed: Mapped[int] = mapped_column(Integer, default=0)
    bytes_read: Mapped[int] = mapped_column(Integer, default=0)
    bytes_written: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    execution_log: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="runs")


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id: Mapped[str] = mapped_column(String, ForeignKey("pipelines.id"), nullable=False)
    check_type: Mapped[str] = mapped_column(String)  # NULL_RATE, ROW_COUNT, SCHEMA, DISTRIBUTION
    column_name: Mapped[str] = mapped_column(String, nullable=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=True)
    actual_value: Mapped[float] = mapped_column(Float, nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="quality_checks")


class LineageNode(Base):
    __tablename__ = "lineage_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id: Mapped[str] = mapped_column(String, ForeignKey("pipelines.id"), nullable=False)
    node_name: Mapped[str] = mapped_column(String, nullable=False)
    node_type: Mapped[str] = mapped_column(String)  # SOURCE, TRANSFORM, DESTINATION
    upstream_nodes: Mapped[list] = mapped_column(JSON, default=list)
    downstream_nodes: Mapped[list] = mapped_column(JSON, default=list)
    columns: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    pipeline: Mapped["Pipeline"] = relationship("Pipeline", back_populates="lineage_nodes")
