from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_admin
from app.models import User
from app.schemas.todo import TodoAdminPage
from app.services import todo_service

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={
        401: {"description": "Token ausente, inválido o vencido"},
        403: {"description": "El usuario no tiene rol admin"},
    },
)


@router.get(
    "/todos",
    response_model=TodoAdminPage,
    summary="Listar las tareas de todos los usuarios",
)
def admin_list_todos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    owner_email: str | None = Query(None, description="Filtra por correo del dueño"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Solo admin. Devuelve tareas de todos los usuarios con los datos del dueño."""
    return todo_service.list_all_todos(db, page, limit, owner_email)
