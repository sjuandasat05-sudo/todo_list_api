import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validar_password(cls, valor: str) -> str:
        if " " in valor:
            raise ValueError("La contraseña no debe contener espacios")
        if not re.search(r"[A-Z]", valor):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", valor):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", valor):
            raise ValueError("La contraseña debe tener al menos un número")
        return valor


class UserPublic(BaseModel):
    """Datos publicos del usuario. Nunca incluye hashed_password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class UserRegistered(UserPublic):
    access_token: str
    token_type: str = "bearer"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
