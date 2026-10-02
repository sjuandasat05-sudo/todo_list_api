import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "todo_list_api"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_list.db")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError("Falta SECRET_KEY en el archivo .env")
