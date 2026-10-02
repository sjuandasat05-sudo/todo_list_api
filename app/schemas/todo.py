from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.category import CategoryOut
from app.schemas.user import UserPublic


class TodoStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class TodoPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


def _validar_fecha(due_date):
    if due_date is not None and due_date < date.today():
        raise ValueError("due_date no puede ser anterior a hoy")


class TodoBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: TodoStatus = TodoStatus.pending
    priority: TodoPriority = TodoPriority.medium
    due_date: date | None = None
    category_id: int | None = None

    @model_validator(mode="after")
    def validar_due_date(self):
        _validar_fecha(self.due_date)
        return self


class TodoCreate(TodoBase):
    pass


class TodoReplace(TodoBase):
    """Cuerpo del PUT: reemplaza todos los campos."""


class TodoPatch(BaseModel):
    """Cuerpo del PATCH: todos los campos son opcionales."""

    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    status: TodoStatus | None = None
    priority: TodoPriority | None = None
    due_date: date | None = None
    category_id: int | None = None

    @model_validator(mode="after")
    def validar_campos(self):
        _validar_fecha(self.due_date)
        for campo in ("title", "status", "priority"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"{campo} no puede ser nulo")
        return self


class TodoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TodoStatus
    priority: TodoPriority
    due_date: date | None
    owner_id: int
    category_id: int | None
    category: CategoryOut | None = None
    created_at: datetime
    updated_at: datetime


class TodoPage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[TodoOut]
    total: int
    page: int
    limit: int


class TodoAdminOut(TodoOut):
    owner: UserPublic


class TodoAdminPage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[TodoAdminOut]
    total: int
    page: int
    limit: int
