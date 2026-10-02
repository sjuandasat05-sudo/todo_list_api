from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models import Todo, User


def get_owned_todo_or_404(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Todo:
    """404 si la tarea no existe y 403 si pertenece a otro usuario."""
    todo = db.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    if todo.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return todo
