"""Orchestrates one tutoring turn: hydrate session state, run the graph, persist."""

import json
import logging
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.features.auth.models import Student
from app.features.tutor.graph import trace
from app.features.tutor.graph.graph import tutor_graph
from app.features.tutor.graph.state import detect_distress, new_state, serialize
from app.features.tutor.models import ConversationHistory, TutorSession
from app.features.tutor.repository import get_conversation, get_session, list_sessions
from app.features.tutor.schemas import (
    AskResponse,
    ConversationMessage,
    ConversationResponse,
    SessionIndexItem,
)

logger = logging.getLogger("app.tutor")

# Assistant `action` -> conversation event `kind` for the transcript / conversation API.
_ACTION_KIND = {
    "diagnostic": "diagnostic_question",
    "hint": "hint",
    "escalation": "escalation",
    "completed": "completed",
    "await": "hint",
}


def _incoming_kind(awaiting: str | None) -> str:
    """Event kind for the student's message this turn."""
    if awaiting == "diagnostic":
        return "diagnostic_answer"
    if awaiting == "hint":
        return "hint_answer"
    return "question"


def _to_transcript(rows: list[ConversationHistory]) -> list[dict]:
    """Map stored rows to the {role, kind, content} transcript the agents consume."""
    return [
        {
            "role": "student" if row.role == "user" else "tutor",
            "kind": row.kind,
            "content": row.content,
        }
        for row in rows
    ]


class SessionNotFoundError(Exception):
    pass


class SessionClosedError(Exception):
    pass


async def ask_question(
    db: AsyncSession,
    student: Student,
    question: str,
    session_id: str | None = None,
    self_rating: int = 3,
    subject_id: str | None = None,
) -> AskResponse:
    if session_id:
        session = await get_session(db, session_id, student.id)
        if session is None:
            raise SessionNotFoundError
        if session.status != "active":
            raise SessionClosedError
        state = (
            dict(session.state)
            if session.state
            else new_state(student.id, session_id, session.concept)
        )
        raw_awaiting = (session.state or {}).get("awaiting")
        # Normalize (legacy sessions stored a bool for "awaiting a hint answer").
        awaiting = (
            "hint"
            if raw_awaiting is True
            else (raw_awaiting if isinstance(raw_awaiting, str) else None)
        )
    else:
        session_id = uuid4().hex[:36]
        session = TutorSession(
            id=session_id,
            student_id=student.id,
            subject_id=subject_id or "1",
            concept=question,
            title=question[:255],
            status="active",
        )
        db.add(session)
        await db.flush()
        state = new_state(student.id, session_id, question)
        awaiting = None

    # Turn inputs
    state["message"] = question
    state["self_rating"] = self_rating
    # `is_answer` drives the evaluator and means "answer to a HINT" only.
    state["is_answer"] = awaiting == "hint"
    state["incoming"] = (
        "diagnostic_answer"
        if awaiting == "diagnostic"
        else "hint_answer"
        if awaiting == "hint"
        else "new"
    )
    state["diag_asked_this_turn"] = False  # transient, reset each turn
    state["distress"] = detect_distress(question)

    # Build the running conversation from prior turns, then append this student message,
    # so every agent in the graph sees the whole session (initial question, diagnostic
    # Q&A, every hint and answer) and never loses context.
    incoming_kind = _incoming_kind(awaiting)
    history = _to_transcript(await get_conversation(db, session_id))
    history.append({"role": "student", "kind": incoming_kind, "content": question})

    db.add(
        ConversationHistory(
            session_id=session_id,
            student_id=student.id,
            role="user",
            kind=incoming_kind,
            content=question,
        )
    )

    trace.start_capture()
    result = await tutor_graph.ainvoke(
        state,
        config={
            "recursion_limit": 60,
            "configurable": {"db": db, "student": student, "history": history},
            "run_name": f"tutor-session:{session_id[:8]}",
            "tags": ["tutor-graph"],
            "metadata": {
                "student_id": student.id,
                "session_id": session_id,
                "is_answer": state["is_answer"],
            },
        },
    )
    agent_io = trace.build_dict()
    if settings.debug_agent_io:
        logger.info(
            "agent I/O for session %s:\n%s",
            session_id,
            json.dumps(agent_io, indent=2, ensure_ascii=False, default=str),
        )
        print(  # noqa: T201 — explicit dev-only console dump of per-agent input/output
            json.dumps(
                {"session_id": session_id, "agents": agent_io},
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            flush=True,
        )

    output = result.get("output", "")
    action = result.get("action", "await")
    db.add(
        ConversationHistory(
            session_id=session_id,
            student_id=student.id,
            role="assistant",
            kind=_ACTION_KIND.get(action, "hint"),
            content=output,
        )
    )

    if action == "diagnostic":
        awaiting_type, session.status = "diagnostic", "active"
    elif action == "hint":
        awaiting_type, session.status = "hint", "active"
    elif action == "escalation":
        awaiting_type, session.status = None, "escalated"
    else:  # completed
        awaiting_type, session.status = None, "completed"
    result["awaiting"] = awaiting_type
    session.hint_rung = result.get("hint_level") or session.hint_rung
    session.leak_checks = result.get("leak_checks", session.leak_checks)
    session.state = serialize(result)

    await db.commit()

    profile = result.get("profile") or {}
    evaluation = result.get("evaluation") or {}
    return AskResponse(
        session_id=session_id,
        action=action if action != "await" else "hint",
        message=output,
        hint_level=result.get("hint_level"),
        correct=evaluation.get("correct"),
        mastery=profile.get("mastery"),
        confidence=profile.get("confidence"),
        next_review=result.get("next_review"),
        agents=agent_io if settings.debug_agent_io else None,
    )


async def get_session_conversation(
    db: AsyncSession, student: Student, session_id: str
) -> ConversationResponse:
    """Return the full typed transcript of one session (owned by the student)."""
    session = await get_session(db, session_id, student.id)
    if session is None:
        raise SessionNotFoundError
    rows = await get_conversation(db, session_id)
    messages = [
        ConversationMessage(
            role="student" if row.role == "user" else "tutor",
            kind=row.kind or _incoming_kind(None),
            content=row.content,
            created_at=row.created_at.isoformat() if row.created_at else None,
        )
        for row in rows
    ]
    return ConversationResponse(
        session_id=session.id,
        subject=(session.state or {}).get("subject"),
        initial_question=session.concept,
        status=session.status,
        messages=messages,
    )


async def list_student_sessions(db: AsyncSession, student: Student) -> list[SessionIndexItem]:
    """Return the student's sessions (most recent first) for a conversation index."""
    sessions = await list_sessions(db, student.id)
    return [
        SessionIndexItem(
            session_id=s.id,
            initial_question=s.concept,
            status=s.status,
            subject=(s.state or {}).get("subject"),
            created_at=s.created_at.isoformat() if s.created_at else None,
        )
        for s in sessions
    ]
