from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.display import initials_of, split_name
from app.features.auth.dependencies import get_current_student
from app.features.auth.models import Student
from app.features.auth.schemas import (
    StudentLogin,
    StudentOut,
    StudentRegister,
    Token,
    UserOut,
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


@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 password-flow token endpoint (used by the Swagger 'Authorize' dialog).

    Send the student's email in the `username` field. Returns the same JWT as /login.
    """
    try:
        student = await authenticate_student(db, form_data.username, form_data.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return Token(access_token=issue_token(student))


@router.get("/me", response_model=UserOut)
async def me(current: Student = Depends(get_current_student)):
    first, last = split_name(current.student_name)
    return UserOut(
        id=current.id,
        student_id=current.student_id,
        first_name=first,
        last_name=last,
        full_name=current.student_name,
        initials=initials_of(current.student_name),
        email=current.email,
        role=current.role,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current: Student = Depends(get_current_student)):
    """Stateless logout hook. JWTs are not server-stored, so the client (or BFF)
    just discards the token/cookie; this endpoint exists so the UI has a clean
    call and future token-revocation has a home."""
    return None
