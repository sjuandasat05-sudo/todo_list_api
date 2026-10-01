"""Crea un usuario administrador o promueve a uno existente.

Uso, desde la raiz del proyecto:
    python -m scripts.create_admin
"""
import getpass

from pydantic import ValidationError
from sqlalchemy import select

from app.auth.security import hash_password
from app.database import SessionLocal
from app.models import User
from app.schemas.user import UserCreate


def main() -> None:
    name = input("Nombre: ").strip()
    email = input("Correo: ").strip()
    password = getpass.getpass("Contraseña: ")

    try:
        datos = UserCreate(name=name, email=email, password=password)
    except ValidationError as error:
        print("Datos inválidos:")
        for e in error.errors():
            print(f" - {e['loc'][-1]}: {e['msg']}")
        return

    with SessionLocal() as db:
        user = db.scalars(select(User).where(User.email == datos.email.lower())).first()
        if user is not None:
            user.role = "admin"
            print(f"El usuario {user.email} ahora es admin.")
        else:
            user = User(
                name=datos.name,
                email=datos.email.lower(),
                hashed_password=hash_password(datos.password),
                role="admin",
            )
            db.add(user)
            print(f"Administrador {user.email} creado.")
        db.commit()


if __name__ == "__main__":
    main()
