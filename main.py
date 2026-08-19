"""
Task Management System API
---------------------------
Entry point. Creates the FastAPI app, registers routers, sets up DB
tables on startup, and adds centralized error handling so clients
always get a consistent JSON error shape instead of raw tracebacks.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from . import models
from .database import engine
from .routers import auth, tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task_manager")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Redynox Task Management API",
    description="Task 1 deliverable: Full-stack Python backend with auth, "
                 "CRUD, database relationships, and REST endpoints.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Redynox Task Management API"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ---------- Centralized error handling ----------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Turns Pydantic's default 422 body into a clean, predictable shape."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation failed", "details": exc.errors()},
    )


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "A database error occurred. Please try again."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )
