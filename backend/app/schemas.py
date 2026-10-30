from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator

TaskStatus = Literal["Pendiente", "En curso", "Terminada"]
TaskPriority = Literal["Baja", "Media", "Alta"]

ALLOWED_STATUSES = ("Pendiente", "En curso", "Terminada")
ALLOWED_PRIORITIES = ("Baja", "Media", "Alta")
DEFAULT_PRIORITY = "Media"
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
MAX_ATTACHMENTS_PER_TASK = 3
MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024
ALLOWED_ATTACHMENT_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx")
MAX_ASSIGNEE_LENGTH = 60
MAX_TAG_LENGTH = 30
MAX_TAGS_PER_TASK = 5
MAX_LINK_URL_LENGTH = 500
MAX_LINK_LABEL_LENGTH = 60
MAX_LINKS_PER_TASK = 5
MAX_SUBTASKS_PER_TASK = 20

EMPTY_TITLE_MESSAGE = "El título no puede estar vacío ni contener solo espacios"
TOO_LONG_TITLE_MESSAGE = f"El título no puede superar los {MAX_TITLE_LENGTH} caracteres"
TOO_LONG_DESCRIPTION_MESSAGE = (
    f"La descripción no puede superar los {MAX_DESCRIPTION_LENGTH} caracteres"
)
PAST_DUE_DATE_MESSAGE = "La fecha límite no puede ser anterior a hoy"
INVALID_PRIORITY_MESSAGE = "La prioridad debe ser Baja, Media o Alta"
TOO_LONG_ASSIGNEE_MESSAGE = "El responsable no puede superar los 60 caracteres"
EMPTY_TAG_MESSAGE = "La etiqueta no puede estar vacía ni contener solo espacios"
TOO_LONG_TAG_MESSAGE = "La etiqueta no puede superar los 30 caracteres"
TOO_MANY_TAGS_MESSAGE = f"Una tarea no puede tener más de {MAX_TAGS_PER_TASK} etiquetas"
INVALID_LINK_MESSAGE = "El enlace debe comenzar con http:// o https://"
TOO_LONG_LINK_MESSAGE = "El enlace no puede superar los 500 caracteres"
TOO_LONG_LINK_LABEL_MESSAGE = "El nombre del enlace no puede superar los 60 caracteres"
TOO_MANY_LINKS_MESSAGE = f"Una tarea no puede tener más de {MAX_LINKS_PER_TASK} enlaces"
DUPLICATE_LINK_MESSAGE = "El enlace ya está agregado a la tarea"
TOO_MANY_SUBTASKS_MESSAGE = (
    f"Una tarea no puede tener más de {MAX_SUBTASKS_PER_TASK} subtareas"
)


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


def clean_priority(value: str) -> str:
    """Valida la prioridad contra el conjunto permitido."""
    if value not in ALLOWED_PRIORITIES:
        raise ValueError(INVALID_PRIORITY_MESSAGE)
    return value


def clean_assignee(value: Optional[str]) -> str:
    """Normaliza el responsable. Se permite dejar el campo vacío."""
    clean = (value or "").strip()
    if len(clean) > MAX_ASSIGNEE_LENGTH:
        raise ValueError(TOO_LONG_ASSIGNEE_MESSAGE)
    return clean


def clean_tag(value: str) -> str:
    """Normaliza y valida una etiqueta individual."""
    clean = (value or "").strip()
    if not clean:
        raise ValueError(EMPTY_TAG_MESSAGE)
    if len(clean) > MAX_TAG_LENGTH:
        raise ValueError(TOO_LONG_TAG_MESSAGE)
    return clean


def clean_tags(values: list[str]) -> list[str]:
    """Limpia y deduplica etiquetas conservando el orden y la primera grafía."""
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        name = clean_tag(value)
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(name)
    return cleaned


def clean_link_url(value: str) -> str:
    """Valida que la URL sea http/https y respete la longitud máxima."""
    clean = (value or "").strip()
    lowered = clean.lower()
    if not lowered.startswith(("http://", "https://")):
        raise ValueError(INVALID_LINK_MESSAGE)
    if len(clean) > MAX_LINK_URL_LENGTH:
        raise ValueError(TOO_LONG_LINK_MESSAGE)
    return clean


def clean_link_label(value: Optional[str]) -> str:
    """Normaliza el nombre del enlace. Se permite dejarlo vacío."""
    clean = (value or "").strip()
    if len(clean) > MAX_LINK_LABEL_LENGTH:
        raise ValueError(TOO_LONG_LINK_LABEL_MESSAGE)
    return clean


class SubtaskInput(BaseModel):
    """Subtarea anidada al crear una tarea.

    Acepta tanto un objeto ``{"title": ...}`` como un título en texto plano.
    """

    title: str

    @model_validator(mode="before")
    @classmethod
    def coerce_title(cls, value):
        if isinstance(value, str):
            return {"title": value}
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_title(value)


# Alias con el nombre usado en la especificación para el modelo anidado.
SubtaskCreateInput = SubtaskInput


class LinkCreate(BaseModel):
    url: str
    label: Optional[str] = ""

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return clean_link_url(value)

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: Optional[str]) -> str:
        return clean_link_label(value)


class LinkOut(BaseModel):
    id: int
    url: str
    label: str
    created_at: datetime


class ActivityOut(BaseModel):
    id: int
    action: str
    detail: str
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    due_date: Optional[date] = None
    priority: str = DEFAULT_PRIORITY
    assignee: Optional[str] = ""
    subtasks: list[SubtaskInput] = []
    tags: list[str] = []
    links: list[LinkCreate] = []

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

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        return clean_priority(value)

    @field_validator("assignee")
    @classmethod
    def validate_assignee(cls, value: Optional[str]) -> str:
        return clean_assignee(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return clean_tags(value)


class TaskUpdate(BaseModel):
    """Edición de una tarea. La fecha límite sí puede ser pasada."""

    title: str
    description: Optional[str] = ""
    due_date: Optional[date] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None
    links: Optional[list[LinkCreate]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        return clean_title(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> str:
        return clean_description(value)

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        return clean_priority(value) if value is not None else None

    @field_validator("assignee")
    @classmethod
    def validate_assignee(cls, value: Optional[str]) -> Optional[str]:
        return clean_assignee(value) if value is not None else None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        return clean_tags(value) if value is not None else None


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
    priority: str
    assignee: str
    due_date: Optional[date]
    position: int
    created_at: datetime
    overdue: bool
    subtask_total: int
    subtask_done: int
    subtasks: list[SubtaskOut]
    attachments: list[AttachmentOut]
    tags: list[str]
    links: list[LinkOut]
    activity: list[ActivityOut]
