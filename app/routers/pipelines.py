from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.pipeline import Pipeline, PipelineRun, LineageNode
from app.models.user import User
from app.schemas.pipeline import PipelineCreate, PipelineOut, PipelineRunOut, LineageNodeOut
from app.core.dependencies import get_current_user, require_engineer
from app.services.pipeline_execution_service import trigger_pipeline_run

router = APIRouter(prefix="/api/v1/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineOut, status_code=201)
async def create_pipeline(
    data: PipelineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_engineer),
):
    pipeline = Pipeline(**data.model_dump(), created_by=current_user.id)
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)
    return pipeline


@router.get("", response_model=list[PipelineOut])
async def list_pipelines(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Pipeline).order_by(Pipeline.created_at.desc()))
    return result.scalars().all()


@router.post("/{pipeline_id}/trigger", response_model=PipelineRunOut)
async def trigger_run(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return await trigger_pipeline_run(pipeline_id, "MANUAL", db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{pipeline_id}/runs", response_model=list[PipelineRunOut])
async def get_runs(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PipelineRun)
        .where(PipelineRun.pipeline_id == pipeline_id)
        .order_by(PipelineRun.started_at.desc())
    )
    return result.scalars().all()


@router.get("/{pipeline_id}/runs/{run_id}", response_model=PipelineRunOut)
async def get_run_detail(
    pipeline_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PipelineRun)
        .where(PipelineRun.id == run_id, PipelineRun.pipeline_id == pipeline_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
