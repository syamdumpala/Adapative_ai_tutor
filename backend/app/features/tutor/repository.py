"""Async DB helpers used by graph nodes and the service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tutor.models import (
    ConversationHistory,
    EvidenceEvent,
    SessionAnalytics,
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


# Misconfidence Index priors (hackathon-conservative, per the PS#03 report §4.1 / §8 #2):
# P(slip) and P(guess). Âᵢ = 1−P(slip) if the answer was correct, else P(guess).
_MI_P_SLIP = 0.1
_MI_P_GUESS = 0.2


def misconfidence_index(confidence: float, correct: bool) -> float:
    """Per-item Misconfidence Index signal mᵢ = −Cᵢ·(Cᵢ − Âᵢ) (signed).

    Âᵢ = 1−P(slip) if the answer was correct, else P(guess). Sign convention (flipped so
    higher = better, like mastery): positive → mastery / underconfidence; negative →
    confidently wrong (misconception risk). Based on PS#03 §4.1.
    """
    a_hat = (1.0 - _MI_P_SLIP) if correct else _MI_P_GUESS
    c = max(0.0, min(1.0, float(confidence)))
    return round(-c * (c - a_hat), 4)


async def record_session_analytics(db: AsyncSession, session: TutorSession, result: dict) -> None:
    """Upsert one analytics snapshot for a completed session (subject vs mastery vs
    confidence, plus the misconception category) — the grain the analytics charts read.

    One row per session (keyed by session_id); re-completing a session updates it.
    `result` may be the graph state or the final result dict — both carry `profile`,
    `misconception`, and `misconception_detail`.
    """
    profile = result.get("profile") or {}
    detail = result.get("misconception_detail") or {}
    category = result.get("misconception") or detail.get("category")
    if category in (None, "none", ""):
        category = None
    misconception = detail.get("misconception")
    if misconception in (None, "none", ""):
        misconception = None
    mastery = float(profile.get("mastery") or 0.0)
    confidence = float(profile.get("confidence") or 0.0)
    # Signed Misconfidence Index for this snapshot. Analytics is captured when the
    # concept is mastered, so the outcome is correct unless the evaluation says otherwise.
    correct = bool((result.get("evaluation") or {}).get("correct", True))
    mi = misconfidence_index(confidence, correct)

    row = (
        await db.execute(select(SessionAnalytics).where(SessionAnalytics.session_id == session.id))
    ).scalar_one_or_none()
    if row is None:
        db.add(
            SessionAnalytics(
                student_id=session.student_id,
                session_id=session.id,
                subject_id=session.subject_id,
                mastery=mastery,
                confidence=confidence,
                misconception_category=category,
                misconception=misconception,
                misconception_index=mi,
            )
        )
    else:
        row.subject_id = session.subject_id
        row.mastery = mastery
        row.confidence = confidence
        row.misconception_category = category
        row.misconception = misconception
        row.misconception_index = mi


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
