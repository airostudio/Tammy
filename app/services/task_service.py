"""Task service for task and project coordination"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import List, Optional
import uuid

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service for managing tasks and projects"""

    @staticmethod
    async def create_task(db: AsyncSession, task: TaskCreate) -> Task:
        """Create a new task"""
        db_task = Task(
            id=str(uuid.uuid4()),
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            project=task.project,
            category=task.category,
            tags=task.tags,
            assigned_to=task.assigned_to,
        )

        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def get_task(db: AsyncSession, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_tasks(
        db: AsyncSession,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Task]:
        """Get tasks, optionally filtered by user, status and priority.
        Omitting user_id returns tasks across all users (admin use)."""
        query = select(Task)

        if user_id:
            query = query.where(Task.user_id == user_id)
        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)

        query = query.order_by(Task.due_date.asc().nullslast(), Task.priority.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_task(db: AsyncSession, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task"""
        db_task = await TaskService.get_task(db, task_id)
        if not db_task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)

        # If status is set to completed, set completed_at timestamp
        if update_data.get("status") == "completed" and db_task.status != "completed":
            update_data["completed_at"] = datetime.utcnow()
            update_data["progress_percentage"] = 100

        for field, value in update_data.items():
            setattr(db_task, field, value)

        await db.commit()
        await db.refresh(db_task)
        return db_task

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: str) -> bool:
        """Delete a task"""
        db_task = await TaskService.get_task(db, task_id)
        if not db_task:
            return False

        await db.delete(db_task)
        await db.commit()
        return True

    @staticmethod
    async def get_overdue_tasks(db: AsyncSession, user_id: str) -> List[Task]:
        """Get all overdue tasks"""
        now = datetime.utcnow()
        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.status.in_(["pending", "in_progress"]),
            )
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_tasks_by_project(db: AsyncSession, user_id: str, project: str) -> List[Task]:
        """Get all tasks for a specific project"""
        query = select(Task).where(
            and_(Task.user_id == user_id, Task.project == project)
        ).order_by(Task.due_date.asc().nullslast())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_today_tasks(db: AsyncSession, user_id: str) -> List[Task]:
        """Get tasks due today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59)

        query = select(Task).where(
            and_(
                Task.user_id == user_id,
                Task.due_date >= today_start,
                Task.due_date <= today_end,
                Task.status.in_(["pending", "in_progress"]),
            )
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def complete_task(db: AsyncSession, task_id: str) -> Optional[Task]:
        """Mark a task as completed"""
        db_task = await TaskService.get_task(db, task_id)
        if not db_task:
            return None

        db_task.status = "completed"
        db_task.completed_at = datetime.utcnow()
        db_task.progress_percentage = 100

        await db.commit()
        await db.refresh(db_task)
        return db_task
