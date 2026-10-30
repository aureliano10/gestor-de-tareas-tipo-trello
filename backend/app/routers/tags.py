from fastapi import APIRouter

from .. import repository

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[str])
def list_tags() -> list[str]:
    return repository.list_tag_names()
