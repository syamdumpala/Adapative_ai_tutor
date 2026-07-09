from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# Account roles. Students use the tutor; teachers use the dashboard + admin APIs.
ROLES = ("student", "teacher")


class Student(Base):
    """A user account. `role` distinguishes students (learners) from teachers.

    The table keeps its historical name (`students`) and the `student_id` public
    identifier for both roles — for a teacher it is simply their unique handle.
    """

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Public identifier / handle (e.g. roll number). Auto-generated when a client
    # (like the sign-up form) does not supply one.
    student_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    student_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(
        String(16), default="student", server_default="student", index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
