from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.api.deps import get_current_user
from app.models.user import User
from fastapi import BackgroundTasks

router = APIRouter(prefix="/tasks", tags=["tasks"])

# DB dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

async def send_task_email(email: str, title: str):
    print(f"Sending email to {email}: Task '{title}' created successfully!")

@router.post("/", response_model=TaskOut)
async def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = Task(**payload.dict(), user_id=current_user.id)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # background email
    background_tasks.add_task(send_task_email, current_user.email, task.title)

    return task

@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    is_completed: bool | None = None,
):
    query = select(Task).where(Task.user_id == current_user.id)

    if is_completed is not None:
        query = query.where(Task.is_completed == is_completed)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).where(Task.id == task_id and Task.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).where(Task.id == task_id and Task.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Task).where(Task.id == task_id and Task.user_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return None
