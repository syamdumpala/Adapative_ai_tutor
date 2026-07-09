"""Read/query services for the tutor feature.

Feeds the student-facing surfaces the UI renders: the "Your chats" rail
(sessions list), a single conversation's history (messages), and the student
profile + performance record. Kept separate from ``service.ask_question`` (the
write path that runs the graph) so the read model stays simple.
"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.query import ListParams, Page, apply_search, apply_sort, paginate
from app.features.auth.models import Student
from app.features.catalog.models import Subject
from app.features.tutor.models import (
    ConversationHistory,
    Misconception,
    StudentConceptState,
    TutorSession,
)
from app.features.tutor.schemas import (
    MessageOut,
    MisconceptionRef,
    PerfInsight,
    PerformanceOut,
    PerfStat,
    ProfileOut,
    SessionDetail,
    SessionSummary,
    SubjectRef,
)

MASTERED_THRESHOLD = 0.8
_SESSION_SORTS = {
    "updated_at": TutorSession.updated_at,
    "created_at": TutorSession.created_at,
    "title": TutorSession.title,
}


class SessionNotFoundError(Exception):
    pass


def chat_status(engine_status: str) -> str:
    """Map the graph's session status onto the UI's chat status."""
    return "completed" if engine_status == "completed" else "pending"


def _sender(role: str) -> str:
    return "maya" if role == "user" else "tutor"


async def _subject_refs(db: AsyncSession, subject_ids: set[str]) -> dict[str, SubjectRef]:
    ids = {s for s in subject_ids if s}
    if not ids:
        return {}
    rows = (await db.execute(select(Subject).where(Subject.id.in_(ids)))).scalars().all()
    return {s.id: SubjectRef(id=s.id, name=s.name, glyph=s.glyph, tone=s.tone) for s in rows}


async def _message_stats(
    db: AsyncSession, session_ids: list[str]
) -> tuple[dict[str, int], dict[str, str]]:
    """Return (count per session, last message content per session) for a page."""
    if not session_ids:
        return {}, {}
    rows = (
        await db.execute(
            select(
                ConversationHistory.session_id,
                ConversationHistory.content,
                ConversationHistory.created_at,
            )
            .where(ConversationHistory.session_id.in_(session_ids))
            .order_by(ConversationHistory.created_at.asc())
        )
    ).all()
    counts: dict[str, int] = {}
    last: dict[str, str] = {}
    for session_id, content, _created in rows:
        counts[session_id] = counts.get(session_id, 0) + 1
        last[session_id] = content
    return counts, last


async def list_sessions(
    db: AsyncSession,
    student_id: int,
    params: ListParams,
    status: str | None = None,
    subject_id: str | None = None,
) -> Page[SessionSummary]:
    stmt = select(TutorSession).where(TutorSession.student_id == student_id)
    if status == "pending":
        stmt = stmt.where(TutorSession.status.in_(("active", "escalated")))
    elif status == "completed":
        stmt = stmt.where(TutorSession.status == "completed")
    if subject_id is not None:
        stmt = stmt.where(TutorSession.subject_id == subject_id)
    stmt = apply_search(stmt, [TutorSession.title, TutorSession.concept], params.q)
    stmt = apply_sort(stmt, params.sort, _SESSION_SORTS, TutorSession.updated_at.desc())

    rows, total = await paginate(db, stmt, params.limit, params.offset)
    ids = [s.id for s in rows]
    counts, last = await _message_stats(db, ids)
    subjects = await _subject_refs(db, {s.subject_id for s in rows})

    items = [
        SessionSummary(
            id=s.id,
            subject_id=s.subject_id,
            subject=subjects.get(s.subject_id),
            title=s.title or s.concept,
            status=chat_status(s.status),
            hint_rung=s.hint_rung,
            leak_checks=s.leak_checks,
            message_count=counts.get(s.id, 0),
            last_message=last.get(s.id),
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in rows
    ]
    return Page.build(items, total, params.limit, params.offset)


async def _load_owned_session(db: AsyncSession, session_id: str, viewer: Student) -> TutorSession:
    session = await db.get(TutorSession, session_id)
    # Owner sees their own; a teacher may inspect any. Others get a 404 (no leak).
    if session is None or (session.student_id != viewer.id and viewer.role != "teacher"):
        raise SessionNotFoundError
    return session


async def get_session_detail(db: AsyncSession, session_id: str, viewer: Student) -> SessionDetail:
    session = await _load_owned_session(db, session_id, viewer)
    counts, last = await _message_stats(db, [session_id])
    subjects = await _subject_refs(db, {session.subject_id})
    messages = (
        (
            await db.execute(
                select(ConversationHistory)
                .where(ConversationHistory.session_id == session_id)
                .order_by(ConversationHistory.created_at.asc(), ConversationHistory.id.asc())
            )
        )
        .scalars()
        .all()
    )
    return SessionDetail(
        id=session.id,
        subject_id=session.subject_id,
        subject=subjects.get(session.subject_id),
        title=session.title or session.concept,
        status=chat_status(session.status),
        hint_rung=session.hint_rung,
        leak_checks=session.leak_checks,
        message_count=counts.get(session_id, 0),
        last_message=last.get(session_id),
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[_to_message_out(m) for m in messages],
    )


def _to_message_out(m: ConversationHistory) -> MessageOut:
    return MessageOut(
        id=m.id,
        **{"from": _sender(m.role)},
        kind=m.kind or "text",
        text=m.content,
        payload=m.payload,
        created_at=m.created_at,
    )


async def list_messages(
    db: AsyncSession, session_id: str, viewer: Student, params: ListParams
) -> Page[MessageOut]:
    """Paginated conversation history for one session (oldest first)."""
    await _load_owned_session(db, session_id, viewer)
    stmt = select(ConversationHistory).where(ConversationHistory.session_id == session_id)
    stmt = apply_search(stmt, [ConversationHistory.content], params.q)
    stmt = apply_sort(
        stmt,
        params.sort,
        {"created_at": ConversationHistory.created_at},
        ConversationHistory.id.asc(),
    )
    rows, total = await paginate(db, stmt, params.limit, params.offset)
    return Page.build([_to_message_out(m) for m in rows], total, params.limit, params.offset)


# --- Profile & performance ----------------------------------------------------


async def get_profile(db: AsyncSession, student: Student) -> ProfileOut:
    from app.features.tutor.repository import get_profile as _get_profile

    profile = await _get_profile(db, student.id)
    subjects_available = int(
        (
            await db.execute(
                select(func.count()).select_from(Subject).where(Subject.status == "active")
            )
        ).scalar_one()
    )
    created: datetime = student.created_at
    from app.core.display import initials_of

    return ProfileOut(
        full_name=student.student_name,
        initials=initials_of(student.student_name),
        role_label=student.role.capitalize(),
        grade=(profile.grade if profile else None),
        email=student.email,
        member_since=created.strftime("%b %Y"),
        subjects_available=subjects_available,
    )


async def _recent_accuracy(db: AsyncSession, student_id: int, limit: int = 20) -> float | None:
    from app.features.tutor.models import EvidenceEvent

    rows = (
        (
            await db.execute(
                select(EvidenceEvent.correct)
                .where(EvidenceEvent.student_id == student_id)
                .order_by(EvidenceEvent.created_at.desc())
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )
    if not rows:
        return None
    return sum(1 for c in rows if c) / len(rows)


async def get_performance(db: AsyncSession, student: Student) -> PerformanceOut:
    from app.features.tutor.repository import get_profile as _get_profile

    profile = await _get_profile(db, student.id)

    accuracy = profile.recent_accuracy if profile and profile.recent_accuracy is not None else None
    if accuracy is None:
        accuracy = await _recent_accuracy(db, student.id)
    accuracy_pct = round((accuracy or 0.0) * 100)

    if profile and profile.concepts_mastered is not None:
        mastered = profile.concepts_mastered
    else:
        mastered = int(
            (
                await db.execute(
                    select(func.count())
                    .select_from(StudentConceptState)
                    .where(
                        StudentConceptState.student_id == student.id,
                        StudentConceptState.mastery >= MASTERED_THRESHOLD,
                    )
                )
            ).scalar_one()
        )

    day_streak = profile.day_streak if profile else 0

    resolving = (
        (
            await db.execute(
                select(Misconception)
                .where(
                    Misconception.student_id == student.id,
                    Misconception.status == "resolving",
                )
                .order_by(Misconception.last_seen.desc())
            )
        )
        .scalars()
        .all()
    )
    active_misc = resolving[0] if resolving else None
    if active_misc is not None:
        insight = PerfInsight(
            text=(
                f"{active_misc.name} is {active_misc.status} — keep practicing and it "
                "will be fully cleared soon."
            ),
            misconception=MisconceptionRef(name=active_misc.name, status=active_misc.status),
        )
    else:
        insight = PerfInsight(text="Keep going — every answer sharpens your profile.")

    stats = [
        PerfStat(
            key="accuracy",
            label="Recent accuracy",
            value=f"{accuracy_pct}%",
            value_class="text-green",
        ),
        PerfStat(
            key="mastered", label="Concepts mastered", value=str(mastered), value_class="text-ink"
        ),
        PerfStat(
            key="streak", label="Day streak", value=str(day_streak), value_class="text-violet"
        ),
        PerfStat(
            key="misconception",
            label="Misconception resolving",
            value=str(len(resolving)),
            value_class="text-amber",
        ),
    ]
    return PerformanceOut(
        recent_accuracy=f"{accuracy_pct}%",
        concepts_mastered=mastered,
        day_streak=day_streak,
        misconceptions_resolving=len(resolving),
        insight=insight,
        stats=stats,
    )
