from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.models import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email.lower())).first()


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        name=data.name,
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
