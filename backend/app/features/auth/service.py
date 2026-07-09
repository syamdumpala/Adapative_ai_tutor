"""Business logic for the auth feature. Raises domain errors; routes map them to HTTP."""

import re
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.features.auth.models import Student
from app.features.auth.schemas import StudentRegister


class DuplicateStudentError(Exception):
    """A student with the same email or student_id already exists."""


class InvalidCredentialsError(Exception):
    """Email/password combination did not match."""


def _slugify_handle(email: str) -> str:
    """Turn the local part of an email into a candidate public handle."""
    local = email.split("@", 1)[0]
    slug = re.sub(r"[^A-Za-z0-9_-]", "", local).strip("-_")
    return slug or "user"


async def _unique_student_id(db: AsyncSession, base: str) -> str:
    """Return ``base`` if free, else append a short random suffix until unique."""
    candidate = base
    for _ in range(5):
        exists = await db.execute(select(Student.id).where(Student.student_id == candidate))
        if exists.scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{uuid4().hex[:6]}"
    return f"{base}-{uuid4().hex[:12]}"  # extremely unlikely fallback


async def register_student(db: AsyncSession, payload: StudentRegister) -> Student:
    # Uniqueness pre-check on email (and student_id when the client supplied one).
    conflicts = [Student.email == payload.email]
    if payload.student_id is not None:
        conflicts.append(Student.student_id == payload.student_id)
    existing = await db.execute(select(Student).where(or_(*conflicts)))
    if existing.scalar_one_or_none() is not None:
        raise DuplicateStudentError

    student_id = payload.student_id or await _unique_student_id(db, _slugify_handle(payload.email))

    student = Student(
        student_name=payload.student_name,
        student_id=student_id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
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
