from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.llm import LLMConfigError, llm_config_detail, llm_is_configured
from app.features.auth.dependencies import get_current_student
from app.features.auth.models import Student
from app.features.tutor.schemas import (
    AskRequest,
    AskResponse,
    ConversationResponse,
    SessionSummary,
)
from app.features.tutor.service import (
    SessionClosedError,
    SessionNotFoundError,
    ask_question,
    get_session_conversation,
    list_student_sessions,
)

router = APIRouter(prefix="/tutor", tags=["tutor"])


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


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(
    current: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """List the student's tutoring sessions (most recent first)."""
    return await list_student_sessions(db, current)


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
