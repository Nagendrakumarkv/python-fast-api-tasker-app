from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.task import router as task_router

from app.models.task import Base
from app.db.session import engine

app = FastAPI(title="FastAPI Tasker")

# Create tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Register routes
app.include_router(health_router, prefix="/api")
app.include_router(task_router, prefix="/api")
