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
import math
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
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
    SessionAnalytics,
    StudentConceptState,
    StudentProfile,
    TeacherEscalation,
    TutorSession,
)
from app.features.tutor.repository import misconfidence_index

logger = logging.getLogger("app.seed")

DEMO_PASSWORD = "password123"

SUBJECTS = [
    (
        "1",
        "Fractions",
        "½",
        "green",
        "Compare, simplify, add & subtract",
        "7 concepts",
        False,
    ),
    (
        "2",
        "Decimals",
        ".5",
        "violet",
        "Place value, rounding & operations",
        "6 concepts",
        True,
    ),
    (
        "3",
        "Percentages",
        "%",
        "amber",
        "Of a whole, discount & markup",
        "5 concepts",
        False,
    ),
    ("4", "Integers", "±", "coral", "Negatives & the number line", "5 concepts", False),
    ("5", "Geometry", "△", "green", "Angles, area & perimeter", "8 concepts", False),
    (
        "6",
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
        "1",
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
        "2",
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
        "3",
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


# --- Learning-analytics demo series -------------------------------------------
# One backdated, completed session (+ analytics snapshot) per point, so the
# student "My progress" charts (mastery/confidence trend, misconception donut,
# per-subject bars) render against real DB rows instead of an empty state.
#
# handle -> shape: n points, mastery start/end, confidence lead (over-confidence),
# the subjects the points cycle through, and how many early points carry a
# misconception. The curve rises from m0→m1 with a small deterministic wobble.
ANALYTICS_SHAPE = {
    "maya": {
        "n": 12,
        "m0": 0.30,
        "m1": 0.86,
        "lead": 0.10,
        "subjects": ["1", "1", "2"],
        "miscon": 3,
    },
    "priya": {"n": 10, "m0": 0.55, "m1": 0.84, "lead": 0.03, "subjects": ["1", "2"], "miscon": 2},
    "leo": {"n": 9, "m0": 0.40, "m1": 0.73, "lead": 0.06, "subjects": ["1", "1", "5"], "miscon": 3},
    "sam": {"n": 10, "m0": 0.30, "m1": 0.52, "lead": 0.18, "subjects": ["1", "3"], "miscon": 4},
    "rohan": {"n": 11, "m0": 0.15, "m1": 0.34, "lead": 0.22, "subjects": ["1"], "miscon": 5},
}

# Misconception categories cycled into the early points (drive the donut).
MISCON_POOL = [
    "Whole-number bias",
    "Denominator confusion",
    "Equal-parts error",
    "Gap-counting",
]

# Per-subject session titles the backdated points cycle through (for the chat rail).
ANALYTIC_TITLES = {
    "1": [
        "Adding 4/5 and 3/5",
        "Comparing 3/4 and 2/3",
        "Simplifying 6/8",
        "Equivalent fractions",
        "Fractions on a number line",
        "Subtracting 5/6 − 1/3",
    ],
    "2": ["Rounding 3.47", "Ordering decimals", "Adding 1.4 + 0.75", "Decimal place value"],
    "3": ["25% of 80", "A 20% discount", "Percent to a fraction"],
    "5": ["Angles on a line", "Area of a rectangle", "Perimeter of an L-shape"],
}

_DAYS_BETWEEN_POINTS = 4


def _clamp01(value: float) -> float:
    return max(0.05, min(0.98, value))


def _streak_for(understanding: str, attempts: int) -> int:
    """A plausible practice streak from how well a topic is grasped."""
    base = {"yes": 4, "partial": 2, "no": 0}.get(understanding, 0)
    return base + (attempts if understanding == "yes" else 0)


def _analytics_series(shape: dict) -> list[tuple[str, float, float, str | None]]:
    """(subject_id, mastery, confidence, misconception_category) per backdated point."""
    n = shape["n"]
    subjects = shape["subjects"]
    points: list[tuple[str, float, float, str | None]] = []
    for i in range(n):
        frac = i / max(1, n - 1)
        mastery = _clamp01(
            shape["m0"] + (shape["m1"] - shape["m0"]) * frac + 0.04 * math.sin(i * 1.7)
        )
        # Confidence leads mastery early (over-confidence) and converges as they learn.
        confidence = _clamp01(mastery + shape["lead"] * (1 - frac) + 0.03 * math.cos(i * 1.3))
        category = MISCON_POOL[i % len(MISCON_POOL)] if i < shape["miscon"] else None
        points.append(
            (subjects[i % len(subjects)], round(mastery, 3), round(confidence, 3), category)
        )
    return points


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
                    subject_id="1",
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
                streak=_streak_for(understanding, asked),
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
            subject_id="1",
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


async def _seed_session_analytics(db: AsyncSession, spec: dict) -> None:
    """Backdated completed sessions + analytics snapshots for one student's charts.

    Idempotent: skips a student who already has any analytics row, so re-running
    the seed backfills existing demo accounts without duplicating them.
    """
    shape = ANALYTICS_SHAPE.get(spec["handle"])
    student = await _account_exists(db, spec["email"])
    if shape is None or student is None:
        return
    existing = (
        await db.execute(
            select(func.count())
            .select_from(SessionAnalytics)
            .where(SessionAnalytics.student_id == student.id)
        )
    ).scalar_one()
    if existing:
        return

    series = _analytics_series(shape)
    n = len(series)
    now = datetime.now(UTC)
    for i, (subject_id, mastery, confidence, category) in enumerate(series):
        created = now - timedelta(days=(n - 1 - i) * _DAYS_BETWEEN_POINTS, hours=3)
        session_id = f"seed_an_{spec['handle']}_{i:02d}"
        titles = ANALYTIC_TITLES.get(subject_id, ANALYTIC_TITLES["1"])
        title = titles[i % len(titles)]
        db.add(
            TutorSession(
                id=session_id,
                student_id=student.id,
                subject_id=subject_id,
                concept=title,
                title=title,
                status="completed",
                created_at=created,
                updated_at=created,
            )
        )
        await db.flush()
        db.add(
            ConversationHistory(
                session_id=session_id,
                student_id=student.id,
                role="user",
                kind="text",
                content=f"Can you help me with {title.lower()}?",
                created_at=created,
            )
        )
        db.add(
            ConversationHistory(
                session_id=session_id,
                student_id=student.id,
                role="assistant",
                kind="text",
                content="Nice — you reasoned that out yourself. Great session!",
                created_at=created,
            )
        )
        # A flagged early point reads as "confidently wrong" (negative MI = risk);
        # a clean point reads as a correct completion (positive MI). So the index
        # line climbs from risk toward mastery, mirroring the canonical formula.
        db.add(
            SessionAnalytics(
                student_id=student.id,
                session_id=session_id,
                subject_id=subject_id,
                mastery=mastery,
                confidence=confidence,
                misconception_category=category,
                misconception=category,
                misconception_index=misconfidence_index(confidence, correct=category is None),
                created_at=created,
                updated_at=created,
            )
        )


async def seed(db: AsyncSession, *, with_analytics: bool = False) -> None:
    """Seed the demo dataset. `with_analytics` adds the backdated session-analytics
    series that powers the student "My progress" charts — on by default for the real
    seed entrypoint (``make seed``), off for the test fixture whose assertions rely on
    a minimal, fixed number of sessions."""
    await _upsert_catalog(db)
    await _seed_teacher(db)
    for spec in STUDENTS:
        await _seed_student(db, spec)
    if with_analytics:
        for spec in STUDENTS:
            await _seed_session_analytics(db, spec)
    await db.commit()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed(db, with_analytics=True)
    await engine.dispose()
    logger.info("Seed complete. Demo login password: %s", DEMO_PASSWORD)


if __name__ == "__main__":
    asyncio.run(main())
