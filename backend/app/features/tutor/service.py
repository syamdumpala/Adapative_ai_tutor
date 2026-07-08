"""Business logic for the tutor feature."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import Student
from app.features.tutor.models import QuestionLog
from app.features.tutor.pipeline import run_tutor_pipeline


async def ask_question(db: AsyncSession, student: Student, question: str) -> dict:
    """Run the agentic pipeline and persist a log of the interaction."""
    result = await run_tutor_pipeline(question=question, student_name=student.student_name)

    db.add(
        QuestionLog(
            student_id=student.id,
            question=question,
            answer=result["answer"],
        )
    )
    await db.commit()
    return result
