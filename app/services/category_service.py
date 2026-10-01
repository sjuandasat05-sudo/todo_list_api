from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Todo


def create_category(db: Session, user_id: int, name: str) -> Category:
    existe = db.scalars(
        select(Category).where(Category.user_id == user_id, Category.name == name)
    ).first()
    if existe:
        raise HTTPException(
            status_code=409, detail="Ya existe una categoría con ese nombre"
        )
    categoria = Category(name=name, user_id=user_id)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def list_categories(db: Session, user_id: int) -> list[Category]:
    return list(
        db.scalars(
            select(Category).where(Category.user_id == user_id).order_by(Category.name)
        ).all()
    )


def delete_category(db: Session, category_id: int, user_id: int) -> None:
    categoria = db.get(Category, category_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if categoria.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    tareas = db.scalar(
        select(func.count()).select_from(Todo).where(Todo.category_id == category_id)
    )
    if tareas:
        raise HTTPException(status_code=409, detail="La categoría tiene tareas asociadas")
    db.delete(categoria)
    db.commit()
