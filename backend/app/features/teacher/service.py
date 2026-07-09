"""Business logic for the teacher dashboard.

Reads aggregate across the tutor/catalog models — roster, per-student records,
per-topic outcomes, escalations, evidence — and exposes the two write actions
the UI offers (resolve an escalation, simulate a spaced-repetition day).
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.display import improvement_str, initials_of
from app.core.query import ListParams, Page, apply_search, apply_sort, count_total, paginate_rows
from app.features.auth.models import Student
from app.features.catalog.models import Concept
from app.features.teacher.schemas import (
    EngagementOut,
    EscalationOut,
    EvidenceOut,
    ExploredTopicOut,
    OverviewOut,
    SimulateDayOut,
    StudentRecordOut,
    TeacherStudentOut,
    TopicAggregateOut,
    TopicRef,
    TopicStudentOut,
    TopicWithAggregateOut,
)
from app.features.tutor.models import (
    EvidenceEvent,
    StudentConceptState,
    StudentProfile,
    TeacherEscalation,
)

AT_RISK_TONE = "bad"


class StudentNotFoundError(Exception):
    pass


class TopicNotFoundError(Exception):
    pass


class EscalationNotFoundError(Exception):
    pass


async def _resolve_student(db: AsyncSession, public_id: str) -> Student:
    result = await db.execute(
        select(Student).where(Student.student_id == public_id, Student.role == "student")
    )
    student = result.scalar_one_or_none()
    if student is None:
        raise StudentNotFoundError
    return student


def _engagement(state: StudentConceptState) -> EngagementOut:
    return EngagementOut(asked=state.attempts, u=state.understanding, m=round(state.mastery, 3))


# ---- Roster ------------------------------------------------------------------

_ROSTER_SORTS = {
    "name": Student.student_name,
    "improvement": StudentProfile.improvement_pct,
    "status": StudentProfile.status_label,
}


async def list_roster(
    db: AsyncSession,
    params: ListParams,
    tone: str | None = None,
    status: str | None = None,
) -> Page[TeacherStudentOut]:
    stmt = (
        select(Student, StudentProfile)
        .outerjoin(StudentProfile, StudentProfile.student_id == Student.id)
        .where(Student.role == "student")
    )
    if tone is not None:
        stmt = stmt.where(StudentProfile.risk_tone == tone)
    if status is not None:
        stmt = stmt.where(StudentProfile.status_label == status)
    stmt = apply_search(stmt, [Student.student_name, Student.email], params.q)
    stmt = apply_sort(stmt, params.sort, _ROSTER_SORTS, StudentProfile.improvement_pct.desc())

    rows, total = await paginate_rows(db, stmt, params.limit, params.offset)
    ids = [student.id for student, _ in rows]
    counts = await _topics_explored_counts(db, ids)

    items = [
        TeacherStudentOut(
            id=student.student_id,
            name=student.student_name,
            initials=initials_of(student.student_name),
            tone=(profile.risk_tone if profile else "good"),
            status=(profile.status_label if profile else "New"),
            improvement=improvement_str(profile.improvement_pct if profile else 0),
            topics_explored=counts.get(student.id, 0),
        )
        for student, profile in rows
    ]
    return Page.build(items, total, params.limit, params.offset)


async def _topics_explored_counts(db: AsyncSession, student_ids: list[int]) -> dict[int, int]:
    if not student_ids:
        return {}
    rows = (
        await db.execute(
            select(StudentConceptState.student_id, func.count())
            .where(StudentConceptState.student_id.in_(student_ids))
            .group_by(StudentConceptState.student_id)
        )
    ).all()
    return {sid: count for sid, count in rows}


# ---- Student record ----------------------------------------------------------


async def get_student_record(db: AsyncSession, public_id: str) -> StudentRecordOut:
    student = await _resolve_student(db, public_id)
    profile = (
        await db.execute(select(StudentProfile).where(StudentProfile.student_id == student.id))
    ).scalar_one_or_none()
    totals = (
        await db.execute(
            select(func.count(), func.coalesce(func.sum(StudentConceptState.attempts), 0)).where(
                StudentConceptState.student_id == student.id
            )
        )
    ).one()
    topic_count, total_questions = int(totals[0]), int(totals[1])
    return StudentRecordOut(
        id=student.student_id,
        name=student.student_name,
        initials=initials_of(student.student_name),
        tone=(profile.risk_tone if profile else "good"),
        status=(profile.status_label if profile else "New"),
        improvement=improvement_str(profile.improvement_pct if profile else 0),
        topic_count=topic_count,
        total_questions=total_questions,
    )


async def list_student_topics(
    db: AsyncSession, public_id: str, params: ListParams
) -> Page[ExploredTopicOut]:
    student = await _resolve_student(db, public_id)
    stmt = (
        select(Concept, StudentConceptState)
        .join(StudentConceptState, StudentConceptState.concept_id == Concept.id)
        .where(StudentConceptState.student_id == student.id)
    )
    stmt = apply_search(stmt, [Concept.name], params.q)
    stmt = apply_sort(stmt, params.sort, {"name": Concept.name}, Concept.position.asc())
    rows, total = await paginate_rows(db, stmt, params.limit, params.offset)
    items = [
        ExploredTopicOut(
            topic=TopicRef(id=c.id, name=c.name, glyph=c.glyph, tone=c.tone, long=c.long),
            engagement=_engagement(state),
        )
        for c, state in rows
    ]
    return Page.build(items, total, params.limit, params.offset)


# ---- Topics with aggregates --------------------------------------------------

_TOPIC_SORTS = {"position": Concept.position, "name": Concept.name}


async def _aggregates(db: AsyncSession, concept_ids: list[str]) -> dict[str, TopicAggregateOut]:
    """Class-wide {students, questions, understood} for each concept id."""
    if not concept_ids:
        return {}
    rows = (
        await db.execute(
            select(
                StudentConceptState.concept_id,
                func.count(),
                func.coalesce(func.sum(StudentConceptState.attempts), 0),
                func.sum(case((StudentConceptState.understanding == "yes", 1), else_=0)),
            )
            .where(StudentConceptState.concept_id.in_(concept_ids))
            .group_by(StudentConceptState.concept_id)
        )
    ).all()
    out: dict[str, TopicAggregateOut] = {}
    for concept_id, students, questions, understood in rows:
        out[concept_id] = TopicAggregateOut(
            students=int(students), questions=int(questions), understood=int(understood or 0)
        )
    return out


def _topic_with_aggregate(concept: Concept, agg: TopicAggregateOut) -> TopicWithAggregateOut:
    return TopicWithAggregateOut(
        id=concept.id,
        subject_id=concept.subject_id,
        name=concept.name,
        glyph=concept.glyph,
        tone=concept.tone,
        short=concept.short,
        long=concept.long,
        aggregate=agg,
    )


async def list_topics(
    db: AsyncSession, params: ListParams, subject_id: str | None = None
) -> Page[TopicWithAggregateOut]:
    stmt = select(Concept)
    if subject_id is not None:
        stmt = stmt.where(Concept.subject_id == subject_id)
    stmt = apply_search(stmt, [Concept.name, Concept.short], params.q)
    stmt = apply_sort(stmt, params.sort, _TOPIC_SORTS, Concept.position.asc())
    total = await count_total(db, stmt)
    concepts = list(
        (await db.execute(stmt.limit(params.limit).offset(params.offset))).scalars().all()
    )
    aggs = await _aggregates(db, [c.id for c in concepts])
    empty = TopicAggregateOut(students=0, questions=0, understood=0)
    items = [_topic_with_aggregate(c, aggs.get(c.id, empty)) for c in concepts]
    return Page.build(items, total, params.limit, params.offset)


async def get_topic(db: AsyncSession, concept_id: str) -> TopicWithAggregateOut:
    concept = await db.get(Concept, concept_id)
    if concept is None:
        raise TopicNotFoundError
    aggs = await _aggregates(db, [concept_id])
    empty = TopicAggregateOut(students=0, questions=0, understood=0)
    return _topic_with_aggregate(concept, aggs.get(concept_id, empty))


async def list_topic_students(
    db: AsyncSession, concept_id: str, params: ListParams
) -> Page[TopicStudentOut]:
    if await db.get(Concept, concept_id) is None:
        raise TopicNotFoundError
    stmt = (
        select(Student, StudentConceptState)
        .join(StudentConceptState, StudentConceptState.student_id == Student.id)
        .join(StudentProfile, StudentProfile.student_id == Student.id, isouter=True)
        .where(StudentConceptState.concept_id == concept_id, Student.role == "student")
    )
    stmt = apply_search(stmt, [Student.student_name], params.q)
    stmt = apply_sort(
        stmt, params.sort, {"name": Student.student_name}, StudentConceptState.attempts.desc()
    )
    rows, total = await paginate_rows(db, stmt, params.limit, params.offset)
    profiles = await _profiles_for(db, [s.id for s, _ in rows])
    items = [
        TopicStudentOut(
            id=student.student_id,
            name=student.student_name,
            initials=initials_of(student.student_name),
            tone=(profiles.get(student.id) or "good"),
            engagement=_engagement(state),
        )
        for student, state in rows
    ]
    return Page.build(items, total, params.limit, params.offset)


async def _profiles_for(db: AsyncSession, student_ids: list[int]) -> dict[int, str]:
    if not student_ids:
        return {}
    rows = (
        await db.execute(
            select(StudentProfile.student_id, StudentProfile.risk_tone).where(
                StudentProfile.student_id.in_(student_ids)
            )
        )
    ).all()
    return {sid: tone for sid, tone in rows}


# ---- Escalations -------------------------------------------------------------

_ESCALATION_SORTS = {"created_at": TeacherEscalation.created_at, "status": TeacherEscalation.status}


async def list_escalations(
    db: AsyncSession,
    params: ListParams,
    status: str | None = None,
    trigger: str | None = None,
) -> Page[EscalationOut]:
    stmt = select(TeacherEscalation, Student).join(
        Student, Student.id == TeacherEscalation.student_id
    )
    if status is not None:
        stmt = stmt.where(TeacherEscalation.status == status)
    if trigger is not None:
        stmt = stmt.where(TeacherEscalation.trigger == trigger)
    stmt = apply_search(
        stmt,
        [Student.student_name, TeacherEscalation.excerpt, TeacherEscalation.reason],
        params.q,
    )
    stmt = apply_sort(stmt, params.sort, _ESCALATION_SORTS, TeacherEscalation.created_at.desc())
    rows, total = await paginate_rows(db, stmt, params.limit, params.offset)
    items = [_escalation_out(esc, student) for esc, student in rows]
    return Page.build(items, total, params.limit, params.offset)


def _escalation_out(esc: TeacherEscalation, student: Student) -> EscalationOut:
    return EscalationOut(
        id=esc.id,
        student_id=student.student_id,
        student_name=student.student_name,
        session_id=esc.session_id,
        trigger=esc.trigger,
        reason=esc.reason,
        excerpt=esc.excerpt,
        status=esc.status,
        teacher_notes=esc.teacher_notes,
        created_at=esc.created_at,
        resolved_at=esc.resolved_at,
    )


async def resolve_escalation(
    db: AsyncSession, escalation_id: int, teacher_notes: str | None
) -> EscalationOut:
    esc = await db.get(TeacherEscalation, escalation_id)
    if esc is None:
        raise EscalationNotFoundError
    esc.status = "resolved"
    esc.resolved_at = datetime.now(UTC)
    if teacher_notes is not None:
        esc.teacher_notes = teacher_notes
    await db.commit()
    student = await db.get(Student, esc.student_id)
    return _escalation_out(esc, student)


# ---- Evidence ----------------------------------------------------------------


async def list_student_evidence(
    db: AsyncSession,
    public_id: str,
    params: ListParams,
    concept: str | None = None,
    correct: bool | None = None,
) -> Page[EvidenceOut]:
    student = await _resolve_student(db, public_id)
    stmt = select(EvidenceEvent).where(EvidenceEvent.student_id == student.id)
    if concept is not None:
        stmt = stmt.where(EvidenceEvent.concept == concept)
    if correct is not None:
        stmt = stmt.where(EvidenceEvent.correct == correct)
    stmt = apply_search(stmt, [EvidenceEvent.concept, EvidenceEvent.error_type], params.q)
    stmt = apply_sort(
        stmt, params.sort, {"created_at": EvidenceEvent.created_at}, EvidenceEvent.created_at.desc()
    )
    rows, total = await paginate_rows(db, stmt, params.limit, params.offset)
    # single-entity select → rows are EvidenceEvent objects
    items = [
        EvidenceOut(
            id=e.id,
            session_id=e.session_id,
            concept=e.concept,
            correct=e.correct,
            error_type=e.error_type,
            created_at=e.created_at,
        )
        for e in (r[0] for r in rows)
    ]
    return Page.build(items, total, params.limit, params.offset)


# ---- Overview + simulate-day -------------------------------------------------

TEACHER_CONTEXT = {"teacher_name": "Ms. Alvarez", "period": "Period 3", "subject": "Fractions"}


async def get_overview(db: AsyncSession) -> OverviewOut:
    student_count = int(
        (
            await db.execute(
                select(func.count()).select_from(Student).where(Student.role == "student")
            )
        ).scalar_one()
    )
    at_risk = int(
        (
            await db.execute(
                select(func.count())
                .select_from(StudentProfile)
                .where(StudentProfile.risk_tone == AT_RISK_TONE)
            )
        ).scalar_one()
    )
    open_esc = int(
        (
            await db.execute(
                select(func.count())
                .select_from(TeacherEscalation)
                .where(TeacherEscalation.status == "open")
            )
        ).scalar_one()
    )
    return OverviewOut(
        teacher_name=TEACHER_CONTEXT["teacher_name"],
        period=TEACHER_CONTEXT["period"],
        subject=TEACHER_CONTEXT["subject"],
        student_count=student_count,
        at_risk_count=at_risk,
        open_escalations=open_esc,
    )


async def simulate_day(db: AsyncSession) -> SimulateDayOut:
    """Advance the spaced-repetition clock one day: pull every due `next_review`
    forward by a day so revision items resurface (demo control)."""
    states = (
        (
            await db.execute(
                select(StudentConceptState).where(StudentConceptState.next_review.isnot(None))
            )
        )
        .scalars()
        .all()
    )
    for state in states:
        state.next_review = (state.next_review or datetime.now(UTC)) - timedelta(days=1)
    await db.commit()
    return SimulateDayOut(
        advanced=len(states),
        message=f"+1 day simulated — {len(states)} revision dates advanced",
    )
