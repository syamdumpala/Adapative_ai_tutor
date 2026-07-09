import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_STUDENT_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class StudentRegister(BaseModel):
    student_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["student", "teacher"] = "student"
    # Optional public handle. The sign-up form does not collect one, so the server
    # auto-generates a unique id when it is omitted.
    student_id: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("student_name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("student_name must not be blank")
        return v

    @field_validator("student_id")
    @classmethod
    def _validate_student_id(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not _STUDENT_ID_RE.fullmatch(v):
            raise ValueError("student_id may contain only letters, digits, hyphens and underscores")
        return v

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v: str) -> str:
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("password must contain at least one letter and one digit")
        return v


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    student_name: str
    email: EmailStr
    role: str
    created_at: datetime


class UserOut(BaseModel):
    """Identity payload for `/auth/me` — name split into the parts the UI needs."""

    id: int
    student_id: str
    first_name: str
    last_name: str
    full_name: str
    initials: str
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
