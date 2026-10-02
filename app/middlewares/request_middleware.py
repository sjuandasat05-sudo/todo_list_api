import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from app.config import APP_NAME

logger = logging.getLogger("todo_list_api")


class RequestMiddleware(BaseHTTPMiddleware):
    """Agrega cabeceras X-* a cada respuesta y registra cada peticion."""

    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        inicio = time.perf_counter()

        response = await call_next(request)

        duracion = time.perf_counter() - inicio
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duracion:.4f}"
        response.headers["X-App-Name"] = APP_NAME

        logger.info(
            "%s %s -> %s (%.4fs) [%s]",
            request.method,
            request.url.path,
            response.status_code,
            duracion,
            request_id,
        )
        return response
