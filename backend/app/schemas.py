from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

TaskStatus = Literal["Pendiente", "En curso", "Terminada"]

ALLOWED_STATUSES = ("Pendiente", "En curso", "Terminada")
MAX_TITLE_LENGTH = 100


class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if value is None:
            raise ValueError("El título es obligatorio")
        clean_title = value.strip()
        if not clean_title:
            raise ValueError("El título no puede estar vacío ni contener solo espacios")
        if len(clean_title) > MAX_TITLE_LENGTH:
            raise ValueError(
                f"El título no puede superar los {MAX_TITLE_LENGTH} caracteres"
            )
        return clean_title


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskOut(BaseModel):
    id: int
    title: str
    status: TaskStatus
    created_at: datetime
