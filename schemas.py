"""
Pydantic schemas — these are what give us automatic input validation.
Anything that doesn't match these shapes/types is rejected by FastAPI
with a 422 before it ever reaches our business logic.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .models import TaskStatus, TaskPriority


# ---------- User ----------

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Task ----------

class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    """All fields optional -- supports partial updates (PATCH-style via PUT)."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
