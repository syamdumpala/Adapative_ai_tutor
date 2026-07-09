"""Async DB helpers used by graph nodes and the service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tutor.models import (
    ConversationHistory,
    EvidenceEvent,
    StudentProfile,
    TutorSession,
)


async def get_or_create_profile(db: AsyncSession, student_id: int) -> StudentProfile:
    result = await db.execute(select(StudentProfile).where(StudentProfile.student_id == student_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = StudentProfile(
            student_id=student_id,
            mastery=0.3,
            confidence=0.3,
            misconceptions=[],
            evidence_count=0,
        )
        db.add(profile)
        await db.flush()
    return profile


async def get_profile(db: AsyncSession, student_id: int) -> StudentProfile | None:
    result = await db.execute(select(StudentProfile).where(StudentProfile.student_id == student_id))
    return result.scalar_one_or_none()


async def get_session(db: AsyncSession, session_id: str, student_id: int) -> TutorSession | None:
    result = await db.execute(
        select(TutorSession).where(
            TutorSession.id == session_id, TutorSession.student_id == student_id
        )
    )
    return result.scalar_one_or_none()


async def get_conversation(db: AsyncSession, session_id: str) -> list[ConversationHistory]:
    """Return every message of a session in chronological order (for the conversation API
    and to rebuild the agent context each turn)."""
    result = await db.execute(
        select(ConversationHistory)
        .where(ConversationHistory.session_id == session_id)
        .order_by(ConversationHistory.id)
    )
    return list(result.scalars().all())


async def list_sessions(db: AsyncSession, student_id: int) -> list[TutorSession]:
    """Return a student's tutoring sessions, most recent first."""
    result = await db.execute(
        select(TutorSession)
        .where(TutorSession.student_id == student_id)
        .order_by(TutorSession.created_at.desc())
    )
    return list(result.scalars().all())


async def apply_evaluation(
    db: AsyncSession, student_id: int, current_confidence: float, correct: bool
) -> dict:
    """Update the student's long-term profile after ONE evaluated answer.

    Runs on every answer (correct or wrong), so the profile always reflects the
    latest state and the next session fetches the new confidence/mastery.
      - long-term confidence = 0.8*old + 0.2*current   (guide §5)
      - mastery              = 0.8*old + 0.2*(1 if correct else 0), clamped [0,1]
    Returns the updated values as a dict (also mirrored into graph state).
    """
    profile = await get_or_create_profile(db, student_id)
    profile.confidence = round(0.8 * profile.confidence + 0.2 * current_confidence, 3)
    mastery = 0.8 * profile.mastery + 0.2 * (1.0 if correct else 0.0)
    profile.mastery = round(min(1.0, max(0.0, mastery)), 3)
    profile.evidence_count = (profile.evidence_count or 0) + 1
    profile.misconceptions = await consolidate_misconceptions(db, student_id)
    await db.flush()
    return {
        "mastery": profile.mastery,
        "confidence": profile.confidence,
        "misconceptions": profile.misconceptions,
        "evidence_count": profile.evidence_count,
    }


async def consolidate_misconceptions(db: AsyncSession, student_id: int) -> list[str]:
    """Return error types seen >= 2 times (memory rule: no single-mistake storage)."""
    result = await db.execute(
        select(EvidenceEvent.error_type, func.count())
        .where(
            EvidenceEvent.student_id == student_id,
            EvidenceEvent.error_type.is_not(None),
        )
        .group_by(EvidenceEvent.error_type)
    )
    return [
        error_type
        for error_type, count in result.all()
        if error_type and error_type != "none" and count >= 2
    ]
