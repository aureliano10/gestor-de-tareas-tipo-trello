from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator

TaskStatus = Literal["Pendiente", "En curso", "Terminada"]

ALLOWED_STATUSES = ("Pendiente", "En curso", "Terminada")
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
MAX_ATTACHMENTS_PER_TASK = 3
MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024
ALLOWED_ATTACHMENT_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx")

EMPTY_TITLE_MESSAGE = "El título no puede estar vacío ni contener solo espacios"
TOO_LONG_TITLE_MESSAGE = f"El título no puede superar los {MAX_TITLE_LENGTH} caracteres"
TOO_LONG_DESCRIPTION_MESSAGE = (
    f"La descripción no puede superar los {MAX_DESCRIPTION_LENGTH} caracteres"
)
PAST_DUE_DATE_MESSAGE = "La fecha límite no puede ser anterior a hoy"


def clean_title(value: str) -> str:
    """Normaliza y valida el título. Se reutiliza en tareas y subtareas."""
    if value is None:
        raise ValueError("El título es obligatorio")
    clean_title_value = value.strip()
    if not clean_title_value:
        raise ValueError(EMPTY_TITLE_MESSAGE)
    if len(clean_title_value) > MAX_TITLE_LENGTH:
        raise ValueError(TOO_LONG_TITLE_MESSAGE)
    return clean_title_value


def clean_description(value: Optional[str]) -> str:
    clean = (value or "").strip()
    if len(clean) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(TOO_LONG_DESCRIPTION_MESSAGE)
    return clean


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> str:
        return clean_description(value)

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value < date.today():
            raise ValueError(PAST_DUE_DATE_MESSAGE)
        return value


class TaskUpdate(BaseModel):
    """Edición de una tarea. La fecha límite sí puede ser pasada."""

    title: str
    description: Optional[str] = ""
    due_date: Optional[date] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> str:
        return clean_description(value)


class TaskMove(BaseModel):
    status: TaskStatus
    position: Optional[int] = None

    @field_validator("position")
    @classmethod
    def validate_position(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 0:
            raise ValueError("La posición no puede ser negativa")
        return value


class SubtaskCreate(BaseModel):
    title: str
    done: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_title(value)


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        return clean_title(value) if value is not None else None


class SubtaskOut(BaseModel):
    id: int
    title: str
    done: bool
    created_at: datetime


class AttachmentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: TaskStatus
    due_date: Optional[date]
    position: int
    created_at: datetime
    overdue: bool
    subtask_total: int
    subtask_done: int
    subtasks: list[SubtaskOut]
    attachments: list[AttachmentOut]
