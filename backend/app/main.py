import uuid
from contextlib import asynccontextmanager
from time import perf_counter

import structlog
from app.logger import logger, setup_uvicorn_logging
from app.routers import bugs, comments, projects, users
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


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
    setup_uvicorn_logging()
    logger.info("application_started")
    yield
    logger.info("application_stopped")


app = FastAPI(title="DevBug API", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(projects.router)
app.include_router(bugs.router)
app.include_router(comments.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"service": "DevBug", "status": "ok"}
