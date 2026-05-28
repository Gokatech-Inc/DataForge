import random
import time
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pipeline import Pipeline, PipelineRun, LineageNode


TRANSFORM_SPEEDS = {
    "SPARK_SQL": {"rows_per_sec": 500000, "bytes_per_row": 512},
    "DBT": {"rows_per_sec": 100000, "bytes_per_row": 256},
    "PYTHON_UDF": {"rows_per_sec": 50000, "bytes_per_row": 1024},
}


def _simulate_run(pipeline: Pipeline) -> dict:
    """Simulate pipeline execution metrics deterministically."""
    seed = hash(pipeline.id) % 10000
    random.seed(seed)

    config = TRANSFORM_SPEEDS.get(pipeline.transform_type, TRANSFORM_SPEEDS["PYTHON_UDF"])
    base_rows = random.randint(10000, 5000000)
    duration = base_rows / config["rows_per_sec"]
    bytes_read = base_rows * config["bytes_per_row"]
    bytes_written = int(bytes_read * 0.3)  # After compression/filtering

    # 5% chance of failure for simulation realism
    failed = random.random() < 0.05

    return {
        "rows_processed": base_rows if not failed else 0,
        "bytes_read": bytes_read if not failed else 0,
        "bytes_written": bytes_written if not failed else 0,
        "duration_seconds": round(duration, 2),
        "status": "FAILED" if failed else "SUCCESS",
        "error_message": "Simulated transformation error: null constraint violation" if failed else None,
        "execution_log": {
            "stages": [
                {"stage": "source_read", "rows": base_rows, "duration_s": round(duration * 0.3, 2)},
                {"stage": "transform", "rows": base_rows, "duration_s": round(duration * 0.5, 2)},
                {"stage": "destination_write", "rows": base_rows, "duration_s": round(duration * 0.2, 2)},
            ]
        },
    }


def _build_lineage(pipeline: Pipeline) -> list:
    source_node = {
        "node_name": f"{pipeline.source_type.lower()}_source",
        "node_type": "SOURCE",
        "upstream_nodes": [],
        "downstream_nodes": [f"{pipeline.transform_type.lower()}_transform"],
        "columns": ["id", "created_at", "payload"],
    }
    transform_node = {
        "node_name": f"{pipeline.transform_type.lower()}_transform",
        "node_type": "TRANSFORM",
        "upstream_nodes": [f"{pipeline.source_type.lower()}_source"],
        "downstream_nodes": [f"{pipeline.destination_type.lower()}_destination"],
        "columns": ["id", "created_at", "processed_value", "partition_date"],
    }
    dest_node = {
        "node_name": f"{pipeline.destination_type.lower()}_destination",
        "node_type": "DESTINATION",
        "upstream_nodes": [f"{pipeline.transform_type.lower()}_transform"],
        "downstream_nodes": [],
        "columns": ["id", "created_at", "processed_value", "partition_date", "loaded_at"],
    }
    return [source_node, transform_node, dest_node]


async def trigger_pipeline_run(pipeline_id: str, trigger: str, db: AsyncSession) -> PipelineRun:
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    if not pipeline:
        raise ValueError(f"Pipeline {pipeline_id} not found")

    metrics = _simulate_run(pipeline)

    run = PipelineRun(
        pipeline_id=pipeline_id,
        status=metrics["status"],
        trigger=trigger,
        rows_processed=metrics["rows_processed"],
        bytes_read=metrics["bytes_read"],
        bytes_written=metrics["bytes_written"],
        duration_seconds=metrics["duration_seconds"],
        error_message=metrics.get("error_message"),
        execution_log=metrics["execution_log"],
        completed_at=datetime.utcnow(),
    )
    db.add(run)

    # Build lineage on first successful run
    existing_lineage = await db.execute(
        select(LineageNode).where(LineageNode.pipeline_id == pipeline_id)
    )
    if not existing_lineage.scalars().first() and metrics["status"] == "SUCCESS":
        for node_data in _build_lineage(pipeline):
            node = LineageNode(pipeline_id=pipeline_id, **node_data)
            db.add(node)

    await db.commit()
    await db.refresh(run)
    return run
