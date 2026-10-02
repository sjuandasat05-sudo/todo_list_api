import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app import __version__
from app.limiter import limiter
from app.middlewares.request_middleware import RequestMiddleware
from app.routes import admin, auth, categories, todos

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

ORIGENES_PERMITIDOS = ["http://localhost:5173", "http://localhost:3000"]

DESCRIPCION = """
API RESTful para gestionar listas de tareas personales.

* **Autenticación** con JWT (botón **Authorize**: el correo va en `username`).
* **Tareas y categorías** propias de cada usuario, con paginación, filtros y orden.
* **Administración**: el rol `admin` puede consultar las tareas de todos los usuarios.
* **Seguridad**: cabeceras de trazabilidad, CORS y límite de peticiones (429).
"""

tags_metadata = [
    {"name": "Auth", "description": "Registro, inicio de sesión y usuario actual."},
    {"name": "Categories", "description": "Categorías propias de cada usuario."},
    {"name": "Todos", "description": "CRUD de tareas con paginación, filtros y orden."},
    {"name": "Admin", "description": "Consultas exclusivas del rol admin."},
]

app = FastAPI(
    title="todo_list_api",
    description=DESCRIPCION,
    version=__version__,
    openapi_tags=tags_metadata,
    contact={"name": "Tu Nombre", "email": "tu_correo@ejemplo.com"},
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


app.add_middleware(RequestMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time", "X-App-Name"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(todos.router)
app.include_router(admin.router)


@app.get("/", tags=["Root"], summary="Estado de la API")
def root():
    """Comprueba que la API está en ejecución."""
    return {"app": "todo_list_api", "status": "ok"}
