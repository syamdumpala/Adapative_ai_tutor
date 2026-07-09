from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.llm import LLMConfigError, llm_config_detail, llm_is_configured
from app.core.query import ListParams, Page, list_params
from app.features.auth.dependencies import get_current_student, get_current_user
from app.features.auth.models import Student
from app.features.tutor import reads
from app.features.tutor.schemas import (
    AskRequest,
    AskResponse,
    ConversationResponse,
    MessageOut,
    PerformanceOut,
    ProfileOut,
    SessionDetail,
    SessionSummary,
)
from app.features.tutor.service import (
    SessionClosedError,
    SessionNotFoundError,
    ask_question,
    get_session_conversation,
)

router = APIRouter(prefix="/tutor", tags=["tutor"])
me_router = APIRouter(prefix="/me", tags=["me"])


@router.post("/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    current: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Run one turn of the multi-agent tutoring graph.

    Omit `session_id` to start a new session (returns the first hint). Send it back
    with the student's answer to continue the loop (evaluate → next hint / done /
    escalate).
    """
    if not llm_is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM provider is not configured: {llm_config_detail()}",
        )
    try:
        return await ask_question(
            db,
            current,
            payload.question,
            payload.session_id,
            payload.self_rating or 3,
            subject_id=payload.subject_id,
        )
    except LLMConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM provider is not usable: {exc}",
        ) from exc
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        ) from None
    except SessionClosedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session is already completed or escalated; start a new one",
        ) from None


@router.get("/sessions", response_model=Page[SessionSummary])
async def list_sessions(
    params: ListParams = Depends(list_params),
    status_filter: str | None = Query(
        None, alias="status", description="Filter by chat status (pending|completed)"
    ),
    subject_id: str | None = Query(None, description="Filter to one subject"),
    current: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """The student's conversations ("Your chats"): search `q` over title/first message,
    filter by status/subject, sort by recency, paginate."""
    return await reads.list_sessions(
        db, current.id, params, status=status_filter, subject_id=subject_id
    )


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(
    session_id: str,
    current: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """One conversation with its full message history (owner, or any teacher)."""
    try:
        return await reads.get_session_detail(db, session_id, current)
    except reads.SessionNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found") from None


@router.get("/sessions/{session_id}/messages", response_model=Page[MessageOut])
async def list_session_messages(
    session_id: str,
    params: ListParams = Depends(list_params),
    current: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Conversation history for one session (oldest first), paginated + searchable."""
    try:
        return await reads.list_messages(db, session_id, current, params)
    except reads.SessionNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found") from None


@me_router.get("/profile", response_model=ProfileOut)
async def my_profile(
    current: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """The signed-in student's profile card (email, grade, member-since, subjects)."""
    return await reads.get_profile(db, current)


@me_router.get("/performance", response_model=PerformanceOut)
async def my_performance(
    current: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """The student performance record: accuracy, mastery, streak, misconception status."""
    return await reads.get_performance(db, current)


@router.get("/sessions/{session_id}/conversation", response_model=ConversationResponse)
async def get_conversation(
    session_id: str,
    current: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Fetch the full typed conversation for one session: the initial question, every
    diagnostic question/answer, every hint and hint answer, and the outcome."""
    try:
        return await get_session_conversation(db, current, session_id)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        ) from None
