"""Async DB helpers used by graph nodes and the service."""

import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.catalog.models import Concept
from app.features.tutor.models import (
    ConversationHistory,
    EvidenceEvent,
    SessionAnalytics,
    StudentConceptState,
    StudentProfile,
    TutorSession,
)

# Very common words that carry no topic signal (kept tiny — the fallback handles misses).
_STOPWORDS = frozenset(
    {
        "how",
        "the",
        "and",
        "you",
        "what",
        "why",
        "does",
        "this",
        "that",
        "with",
        "for",
        "are",
        "can",
        "not",
        "would",
        "should",
        "when",
        "which",
        "into",
        "your",
        "about",
    }
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


def _keywords(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower()) if len(w) >= 3 and w not in _STOPWORDS}


def _stem_match(a: str, b: str) -> bool:
    """Crude stemmer: two words match if they share a long-enough leading run, so
    'compare'/'comparing' and 'add'/'adding' both count while unrelated words don't."""
    shared = 0
    for ca, cb in zip(a, b, strict=False):
        if ca != cb:
            break
        shared += 1
    return shared >= min(len(a), len(b), 4)


async def resolve_concept_id(db: AsyncSession, subject_id: str | None, question: str) -> str | None:
    """Best-effort map a (subject, free-text question) to a catalog concept id.

    Live sessions are subject-scoped with a free-text question, but per-topic state is
    keyed by concept. Score each of the subject's concepts by prefix-overlap between the
    question and the concept's name+blurb, and pick the best; fall back to the subject's
    first (entry-level) concept when nothing matches. Returns None if the subject has no
    concepts. Deterministic (no LLM) so it stays cheap and testable; can be upgraded to
    an LLM classifier later.
    """
    if not subject_id:
        return None
    concepts = (
        (
            await db.execute(
                select(Concept)
                .where(Concept.subject_id == subject_id)
                .order_by(Concept.position.asc())
            )
        )
        .scalars()
        .all()
    )
    if not concepts:
        return None
    q_words = _keywords(question)
    best, best_score = concepts[0], 0
    for concept in concepts:
        name_words = _keywords(f"{concept.name} {concept.short}")
        score = sum(1 for nw in name_words if any(_stem_match(nw, qw) for qw in q_words))
        if score > best_score:
            best, best_score = concept, score
    return best.id


async def apply_concept_evaluation(
    db: AsyncSession,
    student_id: int,
    concept_id: str,
    current_confidence: float,
    correct: bool,
) -> None:
    """Upsert the per-concept state after ONE evaluated answer — the grain the student's
    By-topic charts (and the teacher roster) read. Mirrors ``apply_evaluation`` but keyed
    by concept: EMA mastery/confidence, an attempt count, a correctness streak, an
    understanding band, and a spaced-repetition ``next_review`` (sooner when shaky).
    """
    row = (
        await db.execute(
            select(StudentConceptState).where(
                StudentConceptState.student_id == student_id,
                StudentConceptState.concept_id == concept_id,
            )
        )
    ).scalar_one_or_none()
    if row is None:
        row = StudentConceptState(
            student_id=student_id, concept_id=concept_id, mastery=0.3, confidence=0.3
        )
        db.add(row)

    row.confidence = round(0.8 * row.confidence + 0.2 * current_confidence, 3)
    row.mastery = round(min(1.0, max(0.0, 0.8 * row.mastery + 0.2 * (1.0 if correct else 0.0))), 3)
    row.attempts = (row.attempts or 0) + 1
    row.streak = (row.streak or 0) + 1 if correct else 0
    row.understanding = "yes" if row.mastery >= 0.66 else "partial" if row.mastery >= 0.4 else "no"
    now = datetime.now(UTC)
    row.last_seen = now
    row.next_review = now + timedelta(days=1 if not correct else 1 + round(row.mastery * 6))
    await db.flush()
