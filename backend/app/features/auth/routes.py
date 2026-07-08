from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.features.auth.dependencies import get_current_student
from app.features.auth.models import Student
from app.features.auth.schemas import (
    StudentLogin,
    StudentOut,
    StudentRegister,
    Token,
)
from app.features.auth.service import (
    DuplicateStudentError,
    InvalidCredentialsError,
    authenticate_student,
    issue_token,
    register_student,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def register(payload: StudentRegister, db: AsyncSession = Depends(get_db)):
    try:
        return await register_student(db, payload)
    except DuplicateStudentError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this email or student ID already exists",
        ) from None


@router.post("/login", response_model=Token)
async def login(payload: StudentLogin, db: AsyncSession = Depends(get_db)):
    try:
        student = await authenticate_student(db, payload.email, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from None
    return Token(access_token=issue_token(student))


@router.get("/me", response_model=StudentOut)
async def me(current: Student = Depends(get_current_student)):
    return current
