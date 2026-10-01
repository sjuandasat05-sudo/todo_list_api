import os

from dotenv import load_dotenv

load_dotenv()

APP_NAME = "todo_list_api"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_list.db")
