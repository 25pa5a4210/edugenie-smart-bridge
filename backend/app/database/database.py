"""
SQLAlchemy engine/session setup.
Uses SQLite for local dev; DATABASE_URL can be swapped for PostgreSQL in
production with zero code changes elsewhere (e.g. postgresql://user:pass@host/db).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on app startup."""
    from app.models import (  # noqa: F401  (import so models register on Base.metadata)
        user, conversation, concept, quiz, summary, learning_path, history
    )
    Base.metadata.create_all(bind=engine)
