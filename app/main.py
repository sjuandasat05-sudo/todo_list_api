from fastapi import FastAPI

from app import __version__
from app.routes import auth

app = FastAPI(
    title="todo_list_api",
    description="API RESTful de lista de tareas",
    version=__version__,
)

app.include_router(auth.router)


@app.get("/", tags=["Root"])
def root():
    return {"app": "todo_list_api", "status": "ok"}
