from fastapi import FastAPI

from app import __version__
from app.routes import admin, auth, categories, todos

app = FastAPI(
    title="todo_list_api",
    description="API RESTful de lista de tareas",
    version=__version__,
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(todos.router)
app.include_router(admin.router)


@app.get("/", tags=["Root"])
def root():
    return {"app": "todo_list_api", "status": "ok"}
