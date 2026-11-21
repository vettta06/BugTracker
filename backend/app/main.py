import uuid
from contextlib import asynccontextmanager
from time import perf_counter
import os

from app.database import engine
from sqlalchemy import text
from fastapi.responses import JSONResponse

import structlog
from app.logger import logger
from app.routers import bugs, comments, projects, users
from fastapi import FastAPI, Request
from prometheus_client import start_http_server
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.base import BaseHTTPMiddleware

APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )

        start = perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(
                "request_failed",
                exc_info=exc,
                method=request.method,
                path=request.url.path,
                client=request.client.host if request.client else None,
            )
            raise
        finally:
            process_time = perf_counter() - start
            status_code = response.status_code if "response" in locals() else 500
            logger.info(
                "request_finished",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=round(process_time * 1000, 2),
            )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    metrics_server, metrics_thread = start_http_server(8001)
    logger.info("application_started")
    yield
    logger.info("application_stopped")

    metrics_server.shutdown()
    metrics_server.server_close()
    metrics_thread.join()


app = FastAPI(title="DevBug API", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(projects.router)
app.include_router(bugs.router)
app.include_router(comments.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"service": "DevBug", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}


@app.get("/live")
def live():
    return {"status": "alive", "version": APP_VERSION}


@app.get("/ready")
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503, content={"status": "not_ready", "version": APP_VERSION}
        )

    return {"status": "ready", "version": APP_VERSION}


Instrumentator().instrument(app)
