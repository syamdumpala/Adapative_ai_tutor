from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1, max_length=4000, description="Initial question, or an answer to a hint"
    )
    session_id: str | None = Field(
        default=None, description="Existing session to continue; omit to start a new one"
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


class SessionSummary(BaseModel):
    session_id: str
    initial_question: str
    subject: str | None = None
    status: str
    created_at: str | None = None
