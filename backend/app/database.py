"""Backward-compatible re-exports. Prefer `from app.db import User, Post, get_db`."""

from app.db import Post, User, get_db, init_db
from app.db.session import Base, SessionLocal, engine

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "User",
    "Post",
]
