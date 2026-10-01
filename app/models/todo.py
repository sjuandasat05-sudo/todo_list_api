from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class Todo(Base):
    __tablename__ = "todos"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'done')", name="ck_todos_status"
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')", name="ck_todos_priority"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    priority = Column(String(10), nullable=False, default="medium")
    due_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    owner = relationship("User", back_populates="todos")
    category = relationship("Category", back_populates="todos")
