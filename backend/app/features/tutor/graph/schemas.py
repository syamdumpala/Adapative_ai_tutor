"""Per-agent response schemas.

Each LLM agent is restricted to emit a JSON object matching one of these models.
`graph.llm.run_agent` enforces the shape: when the chat model supports native
structured output it is passed as `response_format`; otherwise the schema is
appended to the prompt at call time and the reply is validated back into it.

All fields carry defaults so a partial / malformed reply still validates into a
usable object instead of raising.
"""

from pydantic import BaseModel


class DiagnosticQuestion(BaseModel):
    """Diagnostic Agent — one probing question."""

    question: str = ""


class DiagnosticObservations(BaseModel):
    """Diagnostic Agent — consolidated observations after probing."""

    observations: str = ""


class MisconceptionResult(BaseModel):
    """Misconception Agent — the classified difficulty."""

    misconception: str = ""
    category: str = "Unknown"
    confidence: float = 0.0
    evidence: str = ""


class PlannerResult(BaseModel):
    """Tutor Planner — the teaching strategy for the next hint."""

    difficulty: str = ""
    teaching_style: str = ""
    hint_goal: str = ""
    hint_level: int = 1
    reason: str = ""


class HintResult(BaseModel):
    """Hint Agent — one progressive hint."""

    hint: str = ""


class GuardResult(BaseModel):
    """Hint Guard — the approve/reject verdict."""

    verdict: str = "APPROVE"


class EvaluationResult(BaseModel):
    """Evaluator — correctness judgement and feedback."""

    correct: bool = False
    confidence: float = 0.0
    feedback: str = ""
