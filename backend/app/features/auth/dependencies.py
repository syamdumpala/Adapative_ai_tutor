from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.features.auth.models import Student

# HTTP Bearer scheme: clients send `Authorization: Bearer <token>`, where the token
# comes from POST /auth/login. In Swagger's "Authorize" dialog this is a single
# field — paste the access_token from the login response. auto_error=False so a
# missing/malformed header returns 401 (below), not HTTPBearer's default 403.
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_student(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Student:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise credentials_exc
    subject = decode_token(credentials.credentials)
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
