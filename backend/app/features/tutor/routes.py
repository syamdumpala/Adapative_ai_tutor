from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.dependencies import get_current_student
from app.features.auth.models import Student
from app.features.tutor.schemas import AskRequest, AskResponse
from app.features.tutor.service import (
    SessionClosedError,
    SessionNotFoundError,
    ask_question,
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
    # if not settings.anthropic_api_key:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail="ANTHROPIC_API_KEY is not configured on the server",
    #     )
    try:
        return await ask_question(
            db,
            current,
            payload.question,
            payload.session_id,
            payload.self_rating or 3,
        )
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        ) from None
    except SessionClosedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session is already completed or escalated; start a new one",
        ) from None
