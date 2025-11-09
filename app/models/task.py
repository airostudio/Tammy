"""Task model"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Task(Base):
    """Task model for task and project coordination"""

    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    # Task Details
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Priority and Status
    priority = Column(String, default="medium")  # low, medium, high, urgent
    status = Column(String, default="pending", index=True)  # pending, in_progress, completed, cancelled, on_hold

    # Timing
    due_date = Column(DateTime, nullable=True, index=True)
    start_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)

    # Organization
    project = Column(String, nullable=True, index=True)
    category = Column(String, nullable=True)
    tags = Column(JSON, default=list)

    # Assignment
    assigned_to = Column(String, nullable=True)  # Can be a user ID or name
    assigned_by = Column(String, default="tammy")

    # Dependencies
    depends_on = Column(JSON, default=list)  # List of task IDs
    blocks = Column(JSON, default=list)  # List of task IDs this task blocks

    # Reminders and Follow-ups
    reminder_date = Column(DateTime, nullable=True)
    is_reminder_sent = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)

    # Subtasks
    parent_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    has_subtasks = Column(Boolean, default=False)

    # Progress
    progress_percentage = Column(Integer, default=0)

    # Notes and Attachments
    notes = Column(Text, nullable=True)
    attachments = Column(JSON, default=list)  # List of file paths or URLs

    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tasks")
    subtasks = relationship("Task", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Task {self.title} [{self.status}]>"
