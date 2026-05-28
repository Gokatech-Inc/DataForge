import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pipeline import Pipeline, QualityCheck, PipelineRun


CHECK_CONFIGS = [
    {"check_type": "ROW_COUNT", "column_name": None, "threshold": 1000},
    {"check_type": "NULL_RATE", "column_name": "id", "threshold": 0.0},
    {"check_type": "NULL_RATE", "column_name": "payload", "threshold": 0.05},
    {"check_type": "SCHEMA", "column_name": None, "threshold": None},
    {"check_type": "DISTRIBUTION", "column_name": "processed_value", "threshold": 3.0},
]


def _run_check(check_type: str, column: str, threshold, pipeline_id: str) -> dict:
    """Simulate data quality check execution."""
    seed = hash(f"{pipeline_id}-{check_type}-{column}") % 1000
    random.seed(seed)

    if check_type == "ROW_COUNT":
        actual = random.randint(800, 5000000)
        passed = actual >= threshold
        details = f"Row count: {actual:,} (minimum: {threshold:,.0f})"
    elif check_type == "NULL_RATE":
        actual = round(random.uniform(0.0, 0.03), 4)
        passed = actual <= threshold
        details = f"Null rate for '{column}': {actual*100:.2f}% (max: {threshold*100:.1f}%)"
    elif check_type == "SCHEMA":
        actual = 1.0
        passed = True
        details = "Schema validated: all expected columns present with correct types"
    elif check_type == "DISTRIBUTION":
        actual = round(random.uniform(0.5, 4.0), 2)
        passed = actual <= threshold
        details = f"Z-score deviation for '{column}': {actual:.2f} (max: {threshold:.1f})"
    else:
        actual = 1.0
        passed = True
        details = "Check passed"

    return {"actual_value": actual, "passed": passed, "details": details}


async def run_quality_checks(pipeline_id: str, db: AsyncSession) -> list:
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalar_one_or_none()
    if not pipeline:
        raise ValueError(f"Pipeline {pipeline_id} not found")

    checks = []
    for cfg in CHECK_CONFIGS:
        result_data = _run_check(cfg["check_type"], cfg.get("column_name"), cfg.get("threshold"), pipeline_id)
        check = QualityCheck(
            pipeline_id=pipeline_id,
            check_type=cfg["check_type"],
            column_name=cfg.get("column_name"),
            threshold=cfg.get("threshold"),
            actual_value=result_data["actual_value"],
            passed=result_data["passed"],
            details=result_data["details"],
        )
        db.add(check)
        checks.append(check)

    await db.commit()
    for c in checks:
        await db.refresh(c)
    return checks


async def get_quality_report(pipeline_id: str, db: AsyncSession) -> dict:
    result = await db.execute(
        select(QualityCheck)
        .where(QualityCheck.pipeline_id == pipeline_id)
        .order_by(QualityCheck.checked_at.desc())
        .limit(20)
    )
    checks = result.scalars().all()
    if not checks:
        return {"pipeline_id": pipeline_id, "checks": [], "pass_rate": 0.0}

    passed = sum(1 for c in checks if c.passed)
    return {
        "pipeline_id": pipeline_id,
        "total_checks": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "pass_rate": round(passed / len(checks) * 100, 1),
        "checks": checks,
    }
