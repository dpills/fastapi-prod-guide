from datetime import datetime

from pydantic import BaseModel


class Todo(BaseModel):
    title: str
    completed: bool = False


class TodoId(BaseModel):
    id: str


class TodoRecord(TodoId, Todo):
    user: str
    created_date: datetime
    updated_date: datetime


class NotFoundException(BaseModel):
    detail: str = "Not Found"
