"""HTTP routes for the teacher dashboard. Every route requires a teacher account."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.query import ListParams, Page, list_params
from app.features.auth.dependencies import require_teacher
from app.features.teacher import service
from app.features.teacher.schemas import (
    EscalationOut,
    EvidenceOut,
    ExploredTopicOut,
    OverviewOut,
    ResolveEscalationIn,
    SimulateDayOut,
    StudentRecordOut,
    TeacherStudentOut,
    TopicStudentOut,
    TopicWithAggregateOut,
)

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


@router.get("/overview", response_model=OverviewOut)
async def overview(db: AsyncSession = Depends(get_db)):
    """Class context + headline counts for the dashboard header."""
    return await service.get_overview(db)


# ---- Roster + student records ------------------------------------------------


@router.get("/students", response_model=Page[TeacherStudentOut])
async def list_students(
    params: ListParams = Depends(list_params),
    tone: str | None = Query(None, description="Filter by health tone (good|warn|bad)"),
    status_label: str | None = Query(None, alias="status", description="Filter by status label"),
    db: AsyncSession = Depends(get_db),
):
    """Roster: search `q` over name/email, filter by tone/status, sort by improvement/name."""
    return await service.list_roster(db, params, tone=tone, status=status_label)


@router.get("/students/{public_id}", response_model=StudentRecordOut)
async def student_record(public_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await service.get_student_record(db, public_id)
    except service.StudentNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found") from None


@router.get("/students/{public_id}/topics", response_model=Page[ExploredTopicOut])
async def student_topics(
    public_id: str,
    params: ListParams = Depends(list_params),
    db: AsyncSession = Depends(get_db),
):
    """The topics a student has explored, with per-topic mastery (searchable by name)."""
    try:
        return await service.list_student_topics(db, public_id, params)
    except service.StudentNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found") from None


@router.get("/students/{public_id}/evidence", response_model=Page[EvidenceOut])
async def student_evidence(
    public_id: str,
    params: ListParams = Depends(list_params),
    concept: str | None = Query(None, description="Filter to one concept"),
    correct: bool | None = Query(None, description="Filter by correctness"),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.list_student_evidence(
            db, public_id, params, concept=concept, correct=correct
        )
    except service.StudentNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found") from None


# ---- Topics ------------------------------------------------------------------


@router.get("/topics", response_model=Page[TopicWithAggregateOut])
async def list_topics(
    params: ListParams = Depends(list_params),
    subject_id: str | None = Query(None, description="Filter to one subject"),
    db: AsyncSession = Depends(get_db),
):
    """Topics with class-wide aggregates (students / questions / understood)."""
    return await service.list_topics(db, params, subject_id=subject_id)


@router.get("/topics/{concept_id}", response_model=TopicWithAggregateOut)
async def topic_detail(concept_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await service.get_topic(db, concept_id)
    except service.TopicNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found") from None


@router.get("/topics/{concept_id}/students", response_model=Page[TopicStudentOut])
async def topic_students(
    concept_id: str,
    params: ListParams = Depends(list_params),
    db: AsyncSession = Depends(get_db),
):
    """How each student did on one topic (searchable by name)."""
    try:
        return await service.list_topic_students(db, concept_id, params)
    except service.TopicNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found") from None


# ---- Escalations -------------------------------------------------------------


@router.get("/escalations", response_model=Page[EscalationOut])
async def list_escalations(
    params: ListParams = Depends(list_params),
    status_filter: str | None = Query(None, alias="status", description="open | resolved"),
    trigger: str | None = Query(
        None, description="confusion | distress | cheating | low_confidence"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Escalation queue: filter by status/trigger, search name/excerpt, sort by recency."""
    return await service.list_escalations(db, params, status=status_filter, trigger=trigger)


@router.post("/escalations/{escalation_id}/resolve", response_model=EscalationOut)
async def resolve_escalation(
    escalation_id: int,
    payload: ResolveEscalationIn | None = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.resolve_escalation(
            db, escalation_id, payload.teacher_notes if payload else None
        )
    except service.EscalationNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Escalation not found") from None


# ---- Demo control ------------------------------------------------------------


@router.post("/simulate-day", response_model=SimulateDayOut)
async def simulate_day(db: AsyncSession = Depends(get_db)):
    """Advance the spaced-repetition clock by one day (demo control)."""
    return await service.simulate_day(db)
