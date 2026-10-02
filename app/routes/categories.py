from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models import User
from app.schemas.category import CategoryCreate, CategoryOut
from app.services import category_service

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    responses={401: {"description": "Token ausente, inválido o vencido"}},
)


@router.post(
    "",
    response_model=CategoryOut,
    status_code=201,
    summary="Crear una categoría",
    responses={409: {"description": "Ya existe una categoría con ese nombre"}},
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Crea una categoría propia (el nombre es único por usuario)."""
    return category_service.create_category(db, current_user.id, data.name)


@router.get("", response_model=list[CategoryOut], summary="Listar mis categorías")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lista las categorías del usuario autenticado."""
    return category_service.list_categories(db, current_user.id)


@router.delete(
    "/{category_id}",
    status_code=204,
    summary="Eliminar una categoría",
    responses={
        403: {"description": "La categoría es de otro usuario"},
        404: {"description": "Categoría no encontrada"},
        409: {"description": "La categoría tiene tareas asociadas"},
    },
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Elimina la categoría. Responde 409 si todavía tiene tareas."""
    category_service.delete_category(db, category_id, current_user.id)
    return Response(status_code=204)
