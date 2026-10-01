from fastapi import FastAPI

from app import __version__

app = FastAPI(
    title="todo_list_api",
    description="API RESTful de lista de tareas",
    version=__version__,
)


@app.get("/", tags=["Root"])
def root():
    return {"app": "todo_list_api", "status": "ok"}
