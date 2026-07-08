"""Business logic for the auth feature. Raises domain errors; routes map them to HTTP."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.features.auth.models import Student
from app.features.auth.schemas import StudentRegister


class DuplicateStudentError(Exception):
    """A student with the same email or student_id already exists."""


class InvalidCredentialsError(Exception):
    """Email/password combination did not match."""


async def register_student(db: AsyncSession, payload: StudentRegister) -> Student:
    existing = await db.execute(
        select(Student).where(
            or_(
                Student.email == payload.email,
                Student.student_id == payload.student_id,
            )
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise DuplicateStudentError

    student = Student(
        student_name=payload.student_name,
        student_id=payload.student_id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


async def authenticate_student(db: AsyncSession, email: str, password: str) -> Student:
    result = await db.execute(select(Student).where(Student.email == email))
    student = result.scalar_one_or_none()
    if student is None or not verify_password(password, student.hashed_password):
        raise InvalidCredentialsError
    return student


def issue_token(student: Student) -> str:
    return create_access_token(str(student.id))
