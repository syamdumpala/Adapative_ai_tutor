from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudentProfile(Base):
    """Long-term learning state for a student (mastery, confidence, misconceptions).

    Beyond the tutoring signals, it carries the display-facing roster/performance
    fields the dashboards render (status label, risk tone, improvement, streak).
    These are seeded for demo students and derived for live ones.
    """

    __tablename__ = "student_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), unique=True, index=True
    )
    mastery: Mapped[float] = mapped_column(Float, default=0.3)
    confidence: Mapped[float] = mapped_column(Float, default=0.3)
    misconceptions: Mapped[list] = mapped_column(JSON, default=list)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    next_review: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Teacher-roster display fields (health chip + improvement figure).
    status_label: Mapped[str] = mapped_column(String(32), default="New")
    risk_tone: Mapped[str] = mapped_column(String(8), default="good")  # good | warn | bad
    improvement_pct: Mapped[int] = mapped_column(Integer, default=0)

    # Student performance-record fields (Performance modal).
    day_streak: Mapped[int] = mapped_column(Integer, default=0)
    recent_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0..1
    concepts_mastered: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grade: Mapped[str | None] = mapped_column(String(32), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StudentConceptState(Base):
    """Per-student × per-concept mastery — the grain the teacher surface needs.

    One row per (student, concept) the student has actually engaged with (the UI
    treats the collection as a sparse map keyed by concept id).
    """

    __tablename__ = "student_concept_state"
    __table_args__ = (UniqueConstraint("student_id", "concept_id", name="uq_student_concept"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    concept_id: Mapped[str] = mapped_column(
        ForeignKey("concepts.id", ondelete="CASCADE"), index=True
    )
    mastery: Mapped[float] = mapped_column(Float, default=0.0)  # 0..1
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # 0..1
    understanding: Mapped[str] = mapped_column(String(8), default="no")  # yes | partial | no
    attempts: Mapped[int] = mapped_column(Integer, default=0)  # "asked" count
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Misconception(Base):
    """A named misconception held by a student, with an evidence-gated status."""

    __tablename__ = "misconceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    concept_id: Mapped[str | None] = mapped_column(
        ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True, index=True
    )
    label: Mapped[str] = mapped_column(String(32), default="")  # e.g. MISC-FR-01
    name: Mapped[str] = mapped_column(String(128))  # e.g. "Whole-number bias"
    status: Mapped[str] = mapped_column(String(16), default="active")  # active|resolving|resolved
    evidence_count: Mapped[int] = mapped_column(Integer, default=1)
    prereq_concept_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TutorSession(Base):
    """A tutoring session (a "chat"). `state` holds the serialized graph state."""

    __tablename__ = "tutor_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    subject_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    concept: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="active")  # active|completed|escalated
    hint_rung: Mapped[int] = mapped_column(Integer, default=0)
    leak_checks: Mapped[int] = mapped_column(Integer, default=0)
    state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class SessionAnalytics(Base):
    """One analytics snapshot per completed session — the grain the mastery/confidence
    vs subject charts read from. Upserted (one row per session) when a session
    reaches history mode (status="completed")."""

    __tablename__ = "session_analytics"
    __table_args__ = (UniqueConstraint("session_id", name="uq_analytics_session"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"), index=True
    )
    subject_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    mastery: Mapped[float] = mapped_column(Float, default=0.0)  # 0..1
    confidence: Mapped[float] = mapped_column(Float, default=0.0)  # 0..1
    misconception_category: Mapped[str | None] = mapped_column(String(128), nullable=True)
    misconception: Mapped[str | None] = mapped_column(String(255), nullable=True)  # the value/name

    misconception_index: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ConversationHistory(Base):
    """Every user message and assistant response, per session (conversation history)."""

    __tablename__ = "conversation_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"), index=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(16))  # user | assistant
    kind: Mapped[str] = mapped_column(String(16), default="text")  # text|diagnosis|quiz|worked|...
    # Event type for the conversation API: question | diagnostic_question |
    # diagnostic_answer | hint | hint_answer | evaluation | completed | escalation.
    kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # structured card data
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvidenceEvent(Base):
    """Short-term evidence: one record per answer the evaluator checks."""

    __tablename__ = "evidence_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"), index=True
    )
    concept: Mapped[str] = mapped_column(Text)
    correct: Mapped[bool] = mapped_column(Boolean)
    error_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TeacherEscalation(Base):
    """Raised when a student repeatedly fails or shows distress; teacher-resolvable."""

    __tablename__ = "teacher_escalations"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"), index=True
    )
    trigger: Mapped[str | None] = mapped_column(String(32), nullable=True)  # confusion|distress|...
    reason: Mapped[str] = mapped_column(Text)
    excerpt: Mapped[str | None] = mapped_column(String(240), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="open", index=True)  # open | resolved
    teacher_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
