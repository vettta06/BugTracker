from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class UserRead(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True


class BugCreate(BaseModel):
    title: str
    description: str | None = None
    status: Literal["open", "in_progress", "closed"]
    priority: Literal["low", "medium", "high"]
    project_id: int
    assignee_id: int | None = None


class BugRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: Literal["open", "in_progress", "closed"]
    priority: Literal["low", "medium", "high"]
    project_id: int
    assignee_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    text: str
    bug_id: int
    author_id: int


class CommentRead(BaseModel):
    id: int
    text: str
    bug_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True
