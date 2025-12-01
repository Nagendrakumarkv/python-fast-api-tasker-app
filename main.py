from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes.health import router as health_router
from app.api.routes.task import router as task_router
from app.api.routes.auth import router as auth_router

from app.models.task import Base
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="FastAPI Tasker", lifespan=lifespan)

app = FastAPI(title="FastAPI Tasker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
