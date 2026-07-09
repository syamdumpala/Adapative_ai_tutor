"""Reusable building blocks for list endpoints: pagination, sorting, search.

Every list endpoint in the API shares one contract so the frontend can treat
them uniformly:

* **Pagination** — ``limit`` (1..``MAX_LIMIT``, default 20) + ``offset`` (>= 0).
* **Sorting** — ``sort=field`` (ascending) or ``sort=-field`` (descending),
  validated against a per-endpoint allowlist of sortable columns. Unknown
  fields raise a clean 422 rather than being silently ignored.
* **Search** — ``q`` performs a case-insensitive ``ILIKE`` across a set of
  columns chosen per endpoint.
* **Filtering** — explicit, typed query params per resource (each service adds
  its own ``where`` clauses); this module only standardizes the cross-cutting
  concerns above.

List responses are wrapped in :class:`Page`, a generic envelope carrying the
page of ``items`` plus ``total`` / ``limit`` / ``offset`` / ``has_more`` so the
UI can render counts and "load more" without a second request.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

from fastapi import HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import ColumnElement, Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# 422 Unprocessable Content — used as a literal to stay version-agnostic across
# Starlette's constant rename (…_ENTITY → …_CONTENT).
HTTP_422 = 422

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Paginated list envelope returned by every collection endpoint."""

    items: list[T]
    total: int
    limit: int
    offset: int
    has_more: bool

    @classmethod
    def build(cls, items: list[T], total: int, limit: int, offset: int) -> Page[T]:
        return cls(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=offset + len(items) < total,
        )


@dataclass(frozen=True)
class ListParams:
    """Normalized pagination + search + sort parameters for one request."""

    limit: int
    offset: int
    q: str | None
    sort: str | None


def list_params(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT, description="Page size (max 100)"),
    offset: int = Query(0, ge=0, description="Rows to skip before the page"),
    q: str | None = Query(None, max_length=200, description="Case-insensitive search"),
    sort: str | None = Query(
        None,
        max_length=64,
        description="Sort field; prefix with '-' for descending (e.g. '-mastery')",
    ),
) -> ListParams:
    """FastAPI dependency that parses the shared list query parameters."""
    cleaned = q.strip() if q else None
    return ListParams(limit=limit, offset=offset, q=cleaned or None, sort=sort)


def apply_search(stmt: Select, columns: Sequence[ColumnElement], term: str | None) -> Select:
    """Filter ``stmt`` so at least one ``column`` matches ``term`` (ILIKE)."""
    if not term or not columns:
        return stmt
    pattern = f"%{term}%"
    return stmt.where(or_(*(col.ilike(pattern) for col in columns)))


def apply_sort(
    stmt: Select,
    sort: str | None,
    allowed: dict[str, ColumnElement],
    default: ColumnElement,
) -> Select:
    """Order ``stmt`` by a validated ``sort`` token, falling back to ``default``.

    ``sort`` is ``"field"`` (ascending) or ``"-field"`` (descending). ``field``
    must be a key of ``allowed``; anything else is a 422 (fail loud, not silent).
    """
    if not sort:
        return stmt.order_by(default)
    descending = sort.startswith("-")
    field = sort[1:] if descending else sort
    column = allowed.get(field)
    if column is None:
        raise HTTPException(
            status_code=HTTP_422,
            detail=(
                f"Cannot sort by '{field}'. Allowed sort fields: {', '.join(sorted(allowed))}."
            ),
        )
    return stmt.order_by(column.desc() if descending else column.asc())


async def count_total(db: AsyncSession, stmt: Select) -> int:
    """Count the full result set of ``stmt`` (ordering stripped) via a subquery."""
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    return int((await db.execute(count_stmt)).scalar_one())


async def paginate(db: AsyncSession, stmt: Select, limit: int, offset: int) -> tuple[list, int]:
    """Run ``stmt`` for a single page and return ``(rows, total_count)``.

    ``total`` counts the full result set (search/filter applied, pagination
    stripped) so the UI can show totals. Use for single-entity selects.
    """
    total = await count_total(db, stmt)
    rows = list((await db.execute(stmt.limit(limit).offset(offset))).scalars().all())
    return rows, total


async def paginate_rows(
    db: AsyncSession, stmt: Select, limit: int, offset: int
) -> tuple[list, int]:
    """Like :func:`paginate` but for multi-entity selects (returns full rows/tuples)."""
    total = await count_total(db, stmt)
    rows = list((await db.execute(stmt.limit(limit).offset(offset))).all())
    return rows, total
