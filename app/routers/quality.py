from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.pipeline import QualityCheckOut
from app.core.dependencies import get_current_user
from app.services.quality_service import run_quality_checks, get_quality_report

router = APIRouter(prefix="/api/v1/quality", tags=["quality"])


@router.post("/{pipeline_id}", response_model=list[QualityCheckOut])
async def trigger_quality_checks(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return await run_quality_checks(pipeline_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{pipeline_id}")
async def quality_report(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return await get_quality_report(pipeline_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
