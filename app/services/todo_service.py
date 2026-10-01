from enum import Enum

from fastapi import HTTPException
from sqlalchemy import asc, case, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models import Category, Todo, User
from app.schemas.todo import TodoCreate, TodoPriority, TodoReplace, TodoStatus


def _valor(v):
    return v.value if isinstance(v, Enum) else v


def _validar_categoria(db: Session, user_id: int, category_id: int | None) -> None:
    if category_id is None:
        return
    categoria = db.get(Category, category_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if categoria.user_id != user_id:
        raise HTTPException(
            status_code=409, detail="La categoría no pertenece al usuario"
        )


def create_todo(db: Session, owner_id: int, data: TodoCreate) -> Todo:
    _validar_categoria(db, owner_id, data.category_id)
    todo = Todo(
        owner_id=owner_id,
        title=data.title,
        description=data.description,
        status=data.status.value,
        priority=data.priority.value,
        due_date=data.due_date,
        category_id=data.category_id,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def replace_todo(db: Session, todo: Todo, data: TodoReplace) -> Todo:
    _validar_categoria(db, todo.owner_id, data.category_id)
    todo.title = data.title
    todo.description = data.description
    todo.status = data.status.value
    todo.priority = data.priority.value
    todo.due_date = data.due_date
    todo.category_id = data.category_id
    db.commit()
    db.refresh(todo)
    return todo


def patch_todo(db: Session, todo: Todo, cambios: dict) -> Todo:
    _validar_categoria(db, todo.owner_id, cambios.get("category_id"))
    for campo, valor in cambios.items():
        setattr(todo, campo, _valor(valor))
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()


def _columna_orden(sort_by: str):
    if sort_by == "priority":
        return case({"low": 1, "medium": 2, "high": 3}, value=Todo.priority, else_=0)
    return {
        "created_at": Todo.created_at,
        "due_date": Todo.due_date,
        "title": Todo.title,
    }[sort_by]


def list_todos(
    db: Session,
    owner_id: int,
    page: int,
    limit: int,
    status: TodoStatus | None,
    priority: TodoPriority | None,
    search: str | None,
    sort_by: str,
    order: str,
) -> dict:
    consulta = select(Todo).where(Todo.owner_id == owner_id)
    if status is not None:
        consulta = consulta.where(Todo.status == status.value)
    if priority is not None:
        consulta = consulta.where(Todo.priority == priority.value)
    if search:
        patron = f"%{search}%"
        consulta = consulta.where(
            or_(Todo.title.ilike(patron), Todo.description.ilike(patron))
        )

    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    direccion = asc if order == "asc" else desc
    items = db.scalars(
        consulta.order_by(direccion(_columna_orden(sort_by)), Todo.id)
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()
    return {"items": items, "total": total, "page": page, "limit": limit}


def list_all_todos(
    db: Session, page: int, limit: int, owner_email: str | None
) -> dict:
    consulta = select(Todo).join(User, Todo.owner_id == User.id)
    if owner_email:
        consulta = consulta.where(User.email == owner_email.lower())

    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    items = db.scalars(
        consulta.order_by(Todo.id).offset((page - 1) * limit).limit(limit)
    ).all()
    return {"items": items, "total": total, "page": page, "limit": limit}
