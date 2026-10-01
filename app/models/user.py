from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base, utcnow


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'user')", name="ck_users_role"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)

    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")
    categories = relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
