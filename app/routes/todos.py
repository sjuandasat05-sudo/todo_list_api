from fastapi import Request
from app.limiter import limiter
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.todos import get_owned_todo_or_404
from app.models import Todo, User
from app.schemas.todo import (
    TodoCreate,
    TodoOut,
    TodoPage,
    TodoPatch,
    TodoPriority,
    TodoReplace,
    TodoStatus,
)
from app.services import todo_service

router = APIRouter(
    prefix="/todos",
    tags=["Todos"],
    responses={401: {"description": "Token ausente, inválido o vencido"}},
)

RESP_PROPIEDAD = {
    403: {"description": "La tarea es de otro usuario"},
    404: {"description": "Tarea no encontrada"},
}


@router.post(
    "",
    response_model=TodoOut,
    status_code=201,
    summary="Crear una tarea",
    responses={
        404: {"description": "Categoría no encontrada"},
        409: {"description": "La categoría no pertenece al usuario"},
    },
)
@limiter.limit("20/minute")
def create_todo(request: Request, 
    data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea una tarea asociada al usuario del token."""
    return todo_service.create_todo(db, current_user.id, data)


@router.get("", response_model=TodoPage, summary="Listar mis tareas")
@limiter.limit("60/minute")
def list_todos(request: Request, 
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: TodoStatus | None = None,
    priority: TodoPriority | None = None,
    search: str | None = Query(None, min_length=1, max_length=100),
    sort_by: Literal["created_at", "due_date", "priority", "title"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista paginada de las tareas propias, con filtros por `status`, `priority` y
    `search` (título o descripción), y orden con `sort_by` y `order`."""
    return todo_service.list_todos(
        db, current_user.id, page, limit, status, priority, search, sort_by, order
    )


@router.get(
    "/{todo_id}",
    response_model=TodoOut,
    summary="Consultar una tarea",
    responses=RESP_PROPIEDAD,
)
def get_todo(todo: Todo = Depends(get_owned_todo_or_404)):
    """Consulta una tarea propia con su categoría."""
    return todo


@router.put(
    "/{todo_id}",
    response_model=TodoOut,
    summary="Reemplazar una tarea",
    responses=RESP_PROPIEDAD,
)
def replace_todo(
    data: TodoReplace,
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
):
    """Reemplaza title, description, status, priority, due_date y category_id."""
    return todo_service.replace_todo(db, todo, data)


@router.patch(
    "/{todo_id}",
    response_model=TodoOut,
    summary="Actualizar parcialmente una tarea",
    responses={**RESP_PROPIEDAD, 400: {"description": "Cuerpo vacío"}},
)
def patch_todo(
    data: TodoPatch,
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
):
    """Actualiza solo los campos enviados. Responde 400 si el cuerpo va vacío."""
    cambios = data.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(
            status_code=400, detail="Debe enviar al menos un campo para actualizar"
        )
    return todo_service.patch_todo(db, todo, cambios)


@router.delete(
    "/{todo_id}",
    status_code=204,
    summary="Eliminar una tarea",
    responses=RESP_PROPIEDAD,
)
def delete_todo(
    todo: Todo = Depends(get_owned_todo_or_404),
    db: Session = Depends(get_db),
):
    """Elimina la tarea sin cuerpo de respuesta."""
    todo_service.delete_todo(db, todo)
    return Response(status_code=204)
