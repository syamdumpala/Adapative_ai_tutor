"""Async DB helpers used by graph nodes and the service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tutor.models import EvidenceEvent, StudentProfile, TutorSession


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
