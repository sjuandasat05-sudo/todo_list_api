from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.security import create_access_token
from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models import User
from app.schemas.user import Token, UserCreate, UserPublic, UserRegistered
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserRegistered,
    status_code=201,
    summary="Registrar un usuario",
    responses={400: {"description": "El correo ya está registrado"}},
)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Crea el usuario con la contraseña en hash y devuelve sus datos públicos más el token."""
    if user_service.get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    user = user_service.create_user(db, data)
    token = create_access_token(str(user.id))
    publico = UserPublic.model_validate(user).model_dump()
    return UserRegistered(**publico, access_token=token)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    responses={
        401: {"description": "Correo o contraseña incorrectos"},
        403: {"description": "Usuario inactivo"},
    },
)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Recibe el correo en el campo `username` y la contraseña. Devuelve el token JWT."""
    user = user_service.authenticate_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return Token(access_token=create_access_token(str(user.id)))


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Usuario autenticado",
    responses={401: {"description": "Token ausente, inválido o vencido"}},
)
def me(current_user: User = Depends(get_current_active_user)):
    """Devuelve el usuario del token, sin hashed_password."""
    return current_user
