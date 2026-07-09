"""Content catalog models: subjects and the concepts (topics) inside them.

Both use human-readable string slug primary keys (``fractions``, ``partition``)
so the same ids the frontend already relies on survive round-trips through the
API. ``tone`` carries a semantic accent (``green|violet|amber|coral``) rather
than raw CSS classes — the client maps tone → colours.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

TONES = ("green", "violet", "amber", "coral")
DIFFICULTY_BANDS = ("easy", "med", "hard")


class Subject(Base):
    """A learnable subject shown on the student home catalog (e.g. Fractions)."""

    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # slug, e.g. "fractions"
    name: Mapped[str] = mapped_column(String(128))
    glyph: Mapped[str] = mapped_column(String(16))
    tone: Mapped[str] = mapped_column(String(16), default="green")
    description: Mapped[str] = mapped_column(String(255), default="")
    meta: Mapped[str] = mapped_column(String(64), default="")  # free text, e.g. "7 concepts"
    status: Mapped[str] = mapped_column(String(16), default="active")  # active | draft
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Concept(Base):
    """A concept / topic within a subject (e.g. "Equal partitioning")."""

    __tablename__ = "concepts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # slug, e.g. "partition"
    subject_id: Mapped[str] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(128))
    glyph: Mapped[str] = mapped_column(String(16), default="")
    tone: Mapped[str] = mapped_column(String(16), default="green")
    short: Mapped[str] = mapped_column(String(255), default="")
    long: Mapped[str] = mapped_column(Text, default="")
    difficulty_band: Mapped[str] = mapped_column(String(8), default="med")
    position: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
