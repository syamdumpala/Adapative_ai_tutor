from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.features.auth.models import Student

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=True)


async def get_current_student(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Student:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    subject = decode_token(token)
    if subject is None:
        raise credentials_exc
    try:
        student_pk = int(subject)
    except (TypeError, ValueError):
        raise credentials_exc from None

    result = await db.execute(select(Student).where(Student.id == student_pk))
    student = result.scalar_one_or_none()
    if student is None:
        raise credentials_exc
    return student
