import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.database import init_db
from app.routers import (
    ai_assistant,
    auth,
    concepts,
    dashboard,
    history,
    learning_paths,
    quizzes,
    summaries,
    users,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("edugenie")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("EduGenie backend started. Environment=%s", settings.ENVIRONMENT)
    yield
    logger.info("EduGenie backend shutting down.")


app = FastAPI(
    title="EduGenie API",
    description="Google Gemini powered educational assistant - backend API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak internal error details to the client.
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again later."},
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ai_assistant.router)
app.include_router(concepts.router)
app.include_router(quizzes.router)
app.include_router(summaries.router)
app.include_router(learning_paths.router)
app.include_router(dashboard.router)
app.include_router(history.router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "service": "EduGenie API", "docs": "/docs"}


@app.get("/api/health", tags=["Health"], summary="API health check")
def health():
    return {"status": "healthy"}
