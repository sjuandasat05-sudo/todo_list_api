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

app = FastAPI(
    title="todo_list_api",
    description="API RESTful de lista de tareas",
    version=__version__,
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


@app.get("/", tags=["Root"])
def root():
    return {"app": "todo_list_api", "status": "ok"}
