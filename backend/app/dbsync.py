"""Lightweight, additive schema sync for PostgreSQL.

`Base.metadata.create_all` creates *missing tables* but never alters existing
ones — so when a feature adds columns to a table that already exists in a live
Postgres database, those columns are silently absent and queries 500 with
``UndefinedColumnError``.

This module bridges that gap without Alembic: it issues ``ALTER TABLE ... ADD
COLUMN IF NOT EXISTS`` for every column added after the initial schema, plus the
matching indexes. It is **idempotent** and **non-destructive** (only adds), runs
automatically on startup (`app.main`), and is also available as
``python -m app.dbsync`` / ``make migrate``.

Only PostgreSQL is targeted: SQLite (tests / zero-setup dev) starts from an empty
database where ``create_all`` already produces every column, and SQLite does not
support ``ADD COLUMN IF NOT EXISTS`` anyway.
"""

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

logger = logging.getLogger("app.dbsync")

# (table, column, column-definition) — columns added after the original schema.
# Definitions mirror the SQLAlchemy model types so a fresh create_all and a
# migrated database converge on the same shape.
_COLUMNS: list[tuple[str, str, str]] = [
    ("students", "role", "VARCHAR(16) NOT NULL DEFAULT 'student'"),
    ("student_profile", "status_label", "VARCHAR(32) NOT NULL DEFAULT 'New'"),
    ("student_profile", "risk_tone", "VARCHAR(8) NOT NULL DEFAULT 'good'"),
    ("student_profile", "improvement_pct", "INTEGER NOT NULL DEFAULT 0"),
    ("student_profile", "day_streak", "INTEGER NOT NULL DEFAULT 0"),
    ("student_profile", "recent_accuracy", "FLOAT"),
    ("student_profile", "concepts_mastered", "INTEGER"),
    ("student_profile", "grade", "VARCHAR(32)"),
    ("tutor_sessions", "subject_id", "VARCHAR(64)"),
    ("tutor_sessions", "title", "VARCHAR(255)"),
    ("tutor_sessions", "hint_rung", "INTEGER NOT NULL DEFAULT 0"),
    ("tutor_sessions", "leak_checks", "INTEGER NOT NULL DEFAULT 0"),
    ("conversation_history", "kind", "VARCHAR(16) NOT NULL DEFAULT 'text'"),
    ("conversation_history", "payload", "JSON"),
    ("teacher_escalations", "trigger", "VARCHAR(32)"),
    ("teacher_escalations", "excerpt", "VARCHAR(240)"),
    ("teacher_escalations", "status", "VARCHAR(16) NOT NULL DEFAULT 'open'"),
    ("teacher_escalations", "teacher_notes", "TEXT"),
    ("teacher_escalations", "resolved_at", "TIMESTAMP WITH TIME ZONE"),
]

# (index-name, table, column) — matches SQLAlchemy's ix_<table>_<column> naming.
_INDEXES: list[tuple[str, str, str]] = [
    ("ix_students_role", "students", "role"),
    ("ix_tutor_sessions_subject_id", "tutor_sessions", "subject_id"),
    ("ix_teacher_escalations_status", "teacher_escalations", "status"),
]


async def sync_schema(conn: AsyncConnection) -> None:
    """Add any columns/indexes missing from an existing PostgreSQL schema."""
    if conn.dialect.name != "postgresql":
        return
    added = 0
    for table, column, definition in _COLUMNS:
        # Identifiers are quoted (some, e.g. "trigger", are reserved words).
        result = await conn.execute(
            text(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "{column}" {definition}')
        )
        # rowcount is unreliable for DDL; we just log the aggregate attempt count.
        added += 1
        del result
    for name, table, column in _INDEXES:
        await conn.execute(text(f'CREATE INDEX IF NOT EXISTS {name} ON {table} ("{column}")'))
    logger.info("Schema sync complete (%d columns ensured on PostgreSQL).", added)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    # Imported here so `python -m app.dbsync` registers every table on the metadata.
    from app.core.database import Base, engine
    from app.features.auth import models as _auth  # noqa: F401
    from app.features.catalog import models as _catalog  # noqa: F401
    from app.features.tutor import models as _tutor  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await sync_schema(conn)
    await engine.dispose()
    logger.info("Database is up to date.")


if __name__ == "__main__":
    asyncio.run(main())
