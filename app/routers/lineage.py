from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.pipeline import LineageNode
from app.models.user import User
from app.schemas.pipeline import LineageNodeOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/lineage", tags=["lineage"])


@router.get("/{pipeline_id}", response_model=list[LineageNodeOut])
async def get_lineage(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(LineageNode).where(LineageNode.pipeline_id == pipeline_id)
    )
    nodes = result.scalars().all()
    if not nodes:
        raise HTTPException(status_code=404, detail="No lineage data found. Trigger a pipeline run first.")
    return nodes
