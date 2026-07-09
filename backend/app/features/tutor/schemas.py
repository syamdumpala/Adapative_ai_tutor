from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1, max_length=4000, description="Initial question, or an answer to a hint"
    )
    session_id: str | None = Field(
        default=None, description="Existing session to continue; omit to start a new one"
    )
    subject_id: str | None = Field(
        default=None, description="Subject the new session belongs to (defaults to fractions)"
    )
    self_rating: int | None = Field(
        default=None, ge=1, le=5, description="Student self-confidence for this answer (1-5)"
    )

    @field_validator("question")
    @classmethod
    def _strip_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("question must not be blank")
        return v


class AskResponse(BaseModel):
    session_id: str
    action: str  # hint | evaluation | escalation | completed
    message: str
    hint_level: int | None = None
    correct: bool | None = None
    mastery: float | None = None
    confidence: float | None = None
    next_review: str | None = None
    sources: list[str] = []
    # Populated only when DEBUG_AGENT_IO=true: {agent: {input, output}} for this turn.
    agents: dict | None = None


# --- Sessions & conversation history -----------------------------------------


class SubjectRef(BaseModel):
    """Minimal subject info embedded in a session summary for the chat rail."""

    id: str
    name: str
    glyph: str
    tone: str


class SessionSummary(BaseModel):
    id: str
    subject_id: str | None
    subject: SubjectRef | None = None
    title: str
    status: str  # chat status: pending | completed
    hint_rung: int
    leak_checks: int
    message_count: int
    last_message: str | None = None
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    sender: str = Field(alias="from")  # maya | tutor
    kind: str  # text | diagnosis | quiz | worked | hintVisual | revision
    text: str
    payload: dict | None = None
    created_at: datetime


class SessionDetail(SessionSummary):
    messages: list[MessageOut] = []


# --- Student profile & performance record ------------------------------------


class ProfileOut(BaseModel):
    full_name: str
    initials: str
    role_label: str
    grade: str | None
    email: str
    member_since: str  # e.g. "Sep 2025"
    subjects_available: int
    avatar_gradient: str = "violet"


class PerfStat(BaseModel):
    key: str
    label: str
    value: str
    value_class: str


class MisconceptionRef(BaseModel):
    name: str
    status: str


class PerfInsight(BaseModel):
    text: str
    misconception: MisconceptionRef | None = None


class PerformanceOut(BaseModel):
    recent_accuracy: str  # e.g. "84%"
    concepts_mastered: int
    day_streak: int
    misconceptions_resolving: int
    insight: PerfInsight
    stats: list[PerfStat]


class ConversationMessage(BaseModel):
    role: str  # student | tutor
    # question | diagnostic_question | diagnostic_answer | hint | hint_answer |
    # completed | escalation
    kind: str
    content: str
    created_at: str | None = None


class ConversationResponse(BaseModel):
    session_id: str
    initial_question: str
    subject: str | None = None
    status: str
    messages: list[ConversationMessage]
