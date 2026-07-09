"""Graph state and helpers for the multi-agent tutor."""

from typing import Any, TypedDict


class TutorState(TypedDict, total=False):
    # Identity / turn inputs
    student_id: int
    session_id: str
    concept: str  # student's original question
    message: str  # the current student message (question or answer)
    is_answer: bool  # True when `message` is an answer to a HINT (drives the evaluator)
    incoming: str  # "new" | "diagnostic_answer" | "hint_answer"
    self_rating: int  # student self-confidence for this answer (1-5)
    distress: bool

    # Per-session working state (filled by agents)
    profile: dict | None  # {mastery, confidence, misconceptions, evidence_count}
    # Interactive diagnostic phase (doctor-style probing before teaching)
    diagnostic_qa: list  # [{question, answer}] collected probing Q&A
    diagnostic_pending: str | None  # probing question awaiting the student's answer
    diag_asked_this_turn: bool  # transient: a probing question was asked this turn
    diagnostic: dict | None  # final {observations, qa} — set once probing is complete
    misconception: str | None  # difficulty category, or "none"
    misconception_detail: (
        dict | None
    )  # full classification {misconception, category, confidence, evidence}
    tutor_plan: dict | None  # {difficulty, hint_level, plan}
    hint: str | None
    hint_level: int
    hint_attempts: int
    hint_approved: bool
    evaluation: dict | None  # {correct, feedback, current_confidence}
    failures: int
    last_feedback: str | None
    escalation: dict | None
    next_review: str | None

    # Turn output (user-facing)
    action: str  # diagnostic | hint | evaluation | escalation | completed | await
    output: str
    awaiting: str | None  # None | "diagnostic" | "hint" — what the next message answers
    subject: str


def new_state(student_id: int, session_id: str, concept: str) -> TutorState:
    return {
        "student_id": student_id,
        "session_id": session_id,
        "concept": concept,
        "message": concept,
        "is_answer": False,
        "incoming": "new",
        "self_rating": 3,
        "distress": False,
        "profile": None,
        "diagnostic_qa": [],
        "diagnostic_pending": None,
        "diag_asked_this_turn": False,
        "diagnostic": None,
        "misconception": None,
        "misconception_detail": None,
        "tutor_plan": None,
        "hint": None,
        "hint_level": 1,
        "hint_attempts": 0,
        "hint_approved": False,
        "evaluation": None,
        "failures": 0,
        "last_feedback": None,
        "escalation": None,
        "next_review": None,
        "action": "await",
        "output": "",
        "awaiting": None,
        "subject": "Maths",
    }


_DISTRESS_MARKERS = (
    "i give up",
    "giving up",
    "too hard",
    "i can't",
    "i cant",
    "frustrated",
    "this is impossible",
    "i hate",
    "i quit",
)


def detect_distress(message: str) -> bool:
    text = message.lower()
    return any(marker in text for marker in _DISTRESS_MARKERS)


def serialize(state: TutorState) -> dict[str, Any]:
    """Return a JSON-serializable copy for persistence in tutor_sessions.state."""
    return dict(state)
