"""Idempotent demo seed — mirrors the frontend's mock data so both dashboards
look populated against the real API.

Run with:  ``python -m app.seed``  (or ``make seed``).

Re-running is safe: subjects/concepts are upserted by id, and a student's whole
bundle (profile, per-concept mastery, sessions, misconceptions) is created only
when the account does not already exist.

Demo credentials (all): password ``password123``.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import hash_password
from app.features.auth.models import Student

# Import every model so metadata is complete before create_all.
from app.features.catalog import models as _catalog_models  # noqa: F401
from app.features.catalog.models import Concept, Subject
from app.features.tutor.models import (
    ConversationHistory,
    Misconception,
    StudentConceptState,
    StudentProfile,
    TeacherEscalation,
    TutorSession,
)

logger = logging.getLogger("app.seed")

DEMO_PASSWORD = "password123"

SUBJECTS = [
    (
        "fractions",
        "Fractions",
        "½",
        "green",
        "Compare, simplify, add & subtract",
        "7 concepts",
        False,
    ),
    (
        "decimals",
        "Decimals",
        ".5",
        "violet",
        "Place value, rounding & operations",
        "6 concepts",
        True,
    ),
    (
        "percentages",
        "Percentages",
        "%",
        "amber",
        "Of a whole, discount & markup",
        "5 concepts",
        False,
    ),
    ("integers", "Integers", "±", "coral", "Negatives & the number line", "5 concepts", False),
    ("geometry", "Geometry", "△", "green", "Angles, area & perimeter", "8 concepts", False),
    (
        "ratios",
        "Ratios & Rates",
        "a:b",
        "violet",
        "Compare, scale & unit rate",
        "6 concepts",
        False,
    ),
]

CONCEPTS = [
    (
        "partition",
        "Equal partitioning",
        "◐",
        "green",
        "easy",
        "Splitting a whole into equal-sized parts.",
        "Every fraction starts here: a whole cut into parts that are exactly the same size. Students who are shaky on equal partitioning tend to miscount pieces and misread what the bottom number means.",
    ),
    (
        "unit",
        "Unit fractions & part–whole",
        "½",
        "violet",
        "easy",
        "Reading 1/n as one of n equal parts.",
        "Understanding that 1/n names a single part when a whole is split into n equal parts — the bridge between partitioning and naming fractions.",
    ),
    (
        "cmpUnit",
        "Comparing unit fractions",
        "⅕",
        "amber",
        "med",
        "Why 1/5 is smaller than 1/4.",
        "More pieces means smaller pieces. This is where whole-number bias shows up most — students assume 1/5 > 1/4 because 5 > 4.",
    ),
    (
        "cmpAny",
        "Comparing any fractions",
        "⅗",
        "coral",
        "hard",
        "Ordering fractions with different tops and bottoms.",
        "Comparing fractions that differ in both numerator and denominator using benchmarks, common denominators, or equivalent forms.",
    ),
    (
        "equiv",
        "Equivalent fractions",
        "=",
        "green",
        "med",
        "Different fractions naming the same amount.",
        "Recognizing that 1/2, 2/4 and 3/6 all name the same quantity — the foundation for adding unlike denominators later.",
    ),
    (
        "addLike",
        "Adding like denominators",
        "+",
        "violet",
        "med",
        "Combining fractions that share a denominator.",
        "Adding and subtracting fractions when the bottom numbers already match — count the pieces, keep the denominator.",
    ),
]

# name, email, handle, status, tone, improvement%, grade, day_streak, accuracy, mastered,
# eng: {concept: (asked, understanding, mastery)}
STUDENTS = [
    {
        "name": "Maya Chen",
        "email": "maya.chen@school.edu",
        "handle": "maya",
        "status": "Improving",
        "tone": "good",
        "improvement": 38,
        "grade": "Grade 5",
        "day_streak": 6,
        "accuracy": 0.84,
        "mastered": 12,
        "eng": {
            "partition": (3, "yes", 0.7),
            "cmpUnit": (2, "yes", 0.6),
            "cmpAny": (2, "yes", 0.6),
            "equiv": (1, "partial", 0.3),
        },
    },
    {
        "name": "Priya Nair",
        "email": "priya@school.edu",
        "handle": "priya",
        "status": "Steady",
        "tone": "good",
        "improvement": 24,
        "grade": "Grade 5",
        "day_streak": 4,
        "accuracy": None,
        "mastered": None,
        "eng": {
            "partition": (1, "yes", 0.82),
            "cmpAny": (2, "yes", 0.71),
            "equiv": (2, "yes", 0.58),
        },
    },
    {
        "name": "Leo Meyer",
        "email": "leo@school.edu",
        "handle": "leo",
        "status": "Steady",
        "tone": "good",
        "improvement": 18,
        "grade": "Grade 5",
        "day_streak": 3,
        "accuracy": None,
        "mastered": None,
        "eng": {
            "partition": (1, "yes", 0.74),
            "unit": (1, "partial", 0.55),
            "cmpAny": (1, "yes", 0.66),
        },
    },
    {
        "name": "Sam Ortiz",
        "email": "sam@school.edu",
        "handle": "sam",
        "status": "Watch",
        "tone": "warn",
        "improvement": 12,
        "grade": "Grade 5",
        "day_streak": 1,
        "accuracy": None,
        "mastered": None,
        "eng": {
            "partition": (2, "partial", 0.52),
            "cmpAny": (1, "no", 0.4),
            "equiv": (1, "no", 0.28),
        },
    },
    {
        "name": "Rohan Das",
        "email": "rohan@school.edu",
        "handle": "rohan",
        "status": "At risk",
        "tone": "bad",
        "improvement": 6,
        "grade": "Grade 5",
        "day_streak": 0,
        "accuracy": None,
        "mastered": None,
        "eng": {"partition": (1, "partial", 0.3), "cmpAny": (4, "no", 0.15)},
    },
]

# id, subject, title, chat-status, hint_rung, leak_checks, [(role, text), ...]
MAYA_SESSIONS = [
    (
        "seed_f1",
        "fractions",
        "Comparing 1/2 and 1/3",
        "completed",
        0,
        2,
        [
            ("user", "Why is 1/2 bigger than 1/3?"),
            (
                "assistant",
                "Good question! A bigger bottom number means more pieces, so each piece is smaller. Cut a pizza into 3 and each slice is smaller than cutting it into 2.",
            ),
            ("user", "Ohh, so 1/2 is the bigger slice."),
            ("assistant", "Exactly — you rebuilt that yourself. Lovely work today!"),
        ],
    ),
    (
        "seed_d1",
        "decimals",
        "Rounding 3.47 to tenths",
        "completed",
        0,
        1,
        [
            ("user", "How do I round 3.47 to the nearest tenth?"),
            (
                "assistant",
                "Look at the digit just after the tenths place — the 7. Since 7 is 5 or more, the tenths digit rounds up, so 3.47 becomes 3.5. Nicely done!",
            ),
        ],
    ),
    (
        "seed_p1",
        "percentages",
        "What is 25% of 80?",
        "pending",
        1,
        1,
        [
            ("user", "What is 25% of 80?"),
            (
                "assistant",
                "Let’s reason it out rather than jump to the answer. 25% is the same as one quarter — so what would you do to 80 to split it into four equal parts?",
            ),
        ],
    ),
]

_CHAT_TO_ENGINE = {"completed": "completed", "pending": "active"}


async def _upsert_catalog(db: AsyncSession) -> None:
    for pos, (sid, name, glyph, tone, desc, meta, is_new) in enumerate(SUBJECTS):
        if await db.get(Subject, sid) is None:
            db.add(
                Subject(
                    id=sid,
                    name=name,
                    glyph=glyph,
                    tone=tone,
                    description=desc,
                    meta=meta,
                    is_new=is_new,
                    position=pos,
                    status="active",
                )
            )
    for pos, (cid, name, glyph, tone, band, short, long) in enumerate(CONCEPTS):
        if await db.get(Concept, cid) is None:
            db.add(
                Concept(
                    id=cid,
                    subject_id="fractions",
                    name=name,
                    glyph=glyph,
                    tone=tone,
                    short=short,
                    long=long,
                    difficulty_band=band,
                    position=pos,
                )
            )
    await db.flush()


async def _account_exists(db: AsyncSession, email: str) -> Student | None:
    return (await db.execute(select(Student).where(Student.email == email))).scalar_one_or_none()


async def _seed_teacher(db: AsyncSession) -> None:
    if await _account_exists(db, "teacher@school.edu") is None:
        db.add(
            Student(
                student_id="teacher",
                student_name="Ms. Alvarez",
                email="teacher@school.edu",
                hashed_password=hash_password(DEMO_PASSWORD),
                role="teacher",
            )
        )
        await db.flush()


async def _seed_student(db: AsyncSession, spec: dict) -> None:
    if await _account_exists(db, spec["email"]) is not None:
        return  # already seeded; keep re-runs a no-op for this bundle
    student = Student(
        student_id=spec["handle"],
        student_name=spec["name"],
        email=spec["email"],
        hashed_password=hash_password(DEMO_PASSWORD),
        role="student",
    )
    db.add(student)
    await db.flush()

    db.add(
        StudentProfile(
            student_id=student.id,
            mastery=0.3,
            confidence=0.3,
            misconceptions=[],
            evidence_count=0,
            status_label=spec["status"],
            risk_tone=spec["tone"],
            improvement_pct=spec["improvement"],
            day_streak=spec["day_streak"],
            recent_accuracy=spec["accuracy"],
            concepts_mastered=spec["mastered"],
            grade=spec["grade"],
        )
    )
    review = datetime.now(UTC) + timedelta(days=2)
    for concept_id, (asked, understanding, mastery) in spec["eng"].items():
        db.add(
            StudentConceptState(
                student_id=student.id,
                concept_id=concept_id,
                mastery=mastery,
                confidence=mastery,
                understanding=understanding,
                attempts=asked,
                last_seen=datetime.now(UTC),
                next_review=review,
            )
        )
    await db.flush()

    if spec["handle"] == "maya":
        await _seed_maya_extras(db, student)
    if spec["handle"] == "rohan":
        await _seed_rohan_escalation(db, student)


async def _seed_maya_extras(db: AsyncSession, student: Student) -> None:
    db.add(
        Misconception(
            student_id=student.id,
            concept_id="cmpUnit",
            label="MISC-FR-01",
            name="Whole-number bias",
            status="resolving",
            evidence_count=2,
            prereq_concept_id="partition",
        )
    )
    for sid, subject, title, chat_status, rung, leaks, lines in MAYA_SESSIONS:
        db.add(
            TutorSession(
                id=sid,
                student_id=student.id,
                subject_id=subject,
                concept=lines[0][1],
                title=title,
                status=_CHAT_TO_ENGINE[chat_status],
                hint_rung=rung,
                leak_checks=leaks,
            )
        )
        await db.flush()
        for role, text in lines:
            db.add(
                ConversationHistory(
                    session_id=sid, student_id=student.id, role=role, kind="text", content=text
                )
            )


async def _seed_rohan_escalation(db: AsyncSession, student: Student) -> None:
    session_id = "seed_esc_rohan"
    db.add(
        TutorSession(
            id=session_id,
            student_id=student.id,
            subject_id="fractions",
            concept="Comparing 4/5 and 5/6",
            title="Comparing 4/5 and 5/6",
            status="escalated",
            hint_rung=3,
            leak_checks=0,
        )
    )
    await db.flush()
    db.add(
        TeacherEscalation(
            student_id=student.id,
            session_id=session_id,
            trigger="confusion",
            reason="Three consecutive failures after the full hint ladder on comparing fractions.",
            excerpt="i keep getting these wrong, i don't get why 4/5 isn't bigger",
            status="open",
        )
    )


async def seed(db: AsyncSession) -> None:
    await _upsert_catalog(db)
    await _seed_teacher(db)
    for spec in STUDENTS:
        await _seed_student(db, spec)
    await db.commit()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed(db)
    await engine.dispose()
    logger.info("Seed complete. Demo login password: %s", DEMO_PASSWORD)


if __name__ == "__main__":
    asyncio.run(main())
