from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import auth, pipelines, quality, lineage


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="DataForge",
    description="Enterprise Data Engineering & Pipeline Orchestration Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(pipelines.router)
app.include_router(quality.router)
app.include_router(lineage.router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "DataForge"}
