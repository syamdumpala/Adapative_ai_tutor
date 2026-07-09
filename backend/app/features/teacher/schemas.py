"""Response/request schemas for the teacher dashboard APIs."""

from datetime import datetime

from pydantic import BaseModel, Field


class EngagementOut(BaseModel):
    """Per student × topic signal (mirrors the UI's `Engagement`)."""

    asked: int
    u: str  # yes | partial | no
    m: float  # mastery 0..1


class TopicRef(BaseModel):
    id: str
    name: str
    glyph: str
    tone: str
    long: str


class TeacherStudentOut(BaseModel):
    id: str  # public student_id (e.g. "maya")
    name: str
    initials: str
    tone: str  # good | warn | bad
    status: str  # free text (Improving | Steady | Watch | At risk | New)
    improvement: str  # signed string e.g. "+38%"
    topics_explored: int


class StudentRecordOut(BaseModel):
    id: str
    name: str
    initials: str
    tone: str
    status: str
    improvement: str
    topic_count: int
    total_questions: int


class ExploredTopicOut(BaseModel):
    topic: TopicRef
    engagement: EngagementOut


class TopicAggregateOut(BaseModel):
    students: int
    questions: int
    understood: int


class TopicWithAggregateOut(BaseModel):
    id: str
    subject_id: str
    name: str
    glyph: str
    tone: str
    short: str
    long: str
    aggregate: TopicAggregateOut


class TopicStudentOut(BaseModel):
    id: str
    name: str
    initials: str
    tone: str
    engagement: EngagementOut


class EscalationOut(BaseModel):
    id: int
    student_id: str
    student_name: str
    session_id: str
    trigger: str | None
    reason: str
    excerpt: str | None
    status: str  # open | resolved
    teacher_notes: str | None
    created_at: datetime
    resolved_at: datetime | None


class ResolveEscalationIn(BaseModel):
    teacher_notes: str | None = Field(default=None, max_length=2000)


class EvidenceOut(BaseModel):
    id: int
    session_id: str
    concept: str
    correct: bool
    error_type: str | None
    created_at: datetime


class OverviewOut(BaseModel):
    teacher_name: str
    period: str
    subject: str
    student_count: int
    at_risk_count: int
    open_escalations: int


class SimulateDayOut(BaseModel):
    advanced: int
    message: str
