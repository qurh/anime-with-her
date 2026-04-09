from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection, connect
from typing import Iterator


DEFAULT_DATABASE_URL = ":memory:"


def _resolve_sqlite_path(database_url: str) -> str:
    if database_url in {":memory:", "sqlite:///:memory:"}:
        return ":memory:"
    if database_url.startswith("sqlite:///"):
        return database_url.removeprefix("sqlite:///")
    return database_url


def create_session(database_url: str = DEFAULT_DATABASE_URL) -> Connection:
    if "://" in database_url and not database_url.startswith("sqlite:///") and database_url != "sqlite:///:memory:":
        raise ValueError("database_url must be sqlite://, sqlite:///..., or a local file path")
    database_path = _resolve_sqlite_path(database_url)
    if database_path == ":memory:":
        return connect(":memory:")
    return connect(Path(database_path))


SessionLocal = create_session


@contextmanager
def session_scope(database_url: str = DEFAULT_DATABASE_URL) -> Iterator[Connection]:
    session = create_session(database_url)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
