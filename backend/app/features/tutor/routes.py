from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.features.auth.dependencies import get_current_student
from app.features.auth.models import Student
from app.features.tutor.schemas import QuestionRequest, QuestionResponse
from app.features.tutor.service import ask_question

router = APIRouter(prefix="/tutor", tags=["tutor"])


@router.post("/ask", response_model=QuestionResponse)
async def ask(
    payload: QuestionRequest,
    current: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    """Run the agentic tutoring pipeline (LangGraph) for the student's question."""
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ANTHROPIC_API_KEY is not configured on the server",
        )
    result = await ask_question(db, current, payload.question)
    return QuestionResponse(question=payload.question, **result)
