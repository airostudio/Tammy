"""Task API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task"""
    return await TaskService.create_task(db, task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Get a task by ID"""
    task = await TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get tasks, optionally filtered by user. Omitting user_id returns all."""
    return await TaskService.get_user_tasks(db, user_id, status, priority)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """Update a task"""
    updated = await TaskService.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a task"""
    success = await TaskService.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/user/{user_id}/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get overdue tasks"""
    return await TaskService.get_overdue_tasks(db, user_id)


@router.get("/user/{user_id}/today", response_model=List[TaskResponse])
async def get_today_tasks(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get tasks due today"""
    return await TaskService.get_today_tasks(db, user_id)


@router.get("/project/{project}", response_model=List[TaskResponse])
async def get_project_tasks(user_id: str, project: str, db: AsyncSession = Depends(get_db)):
    """Get tasks for a specific project"""
    return await TaskService.get_tasks_by_project(db, user_id, project)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    """Mark a task as completed"""
    task = await TaskService.complete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
