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
from app.features.tutor.repository import get_session
from app.features.tutor.schemas import AskResponse

logger = logging.getLogger("app.tutor")


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
) -> AskResponse:
    if session_id:
        session = await get_session(db, session_id, student.id)
        if session is None:
            raise SessionNotFoundError
        if session.status != "active":
            raise SessionClosedError
        print(dict(session.state))
        state = (
            dict(session.state)
            if session.state
            else new_state(student.id, session_id, session.concept)
        )
        awaiting = bool(session.state and session.state.get("awaiting"))
    else:
        session_id = uuid4().hex[:36]
        session = TutorSession(
            id=session_id, student_id=student.id, concept=question, status="active"
        )
        db.add(session)
        await db.flush()
        state = new_state(student.id, session_id, question)
        awaiting = False

    # Turn inputs
    state["message"] = question
    state["self_rating"] = self_rating
    state["is_answer"] = awaiting  # a message on an awaiting session is an answer
    state["distress"] = detect_distress(question)

    db.add(
        ConversationHistory(
            session_id=session_id, student_id=student.id, role="user", content=question
        )
    )

    trace.start_capture()
    result = await tutor_graph.ainvoke(
        state,
        config={
            "recursion_limit": 60,
            "configurable": {"db": db, "student": student},
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
    db.add(
        ConversationHistory(
            session_id=session_id, student_id=student.id, role="assistant", content=output
        )
    )

    action = result.get("action", "await")
    result["awaiting"] = action == "hint"
    session.state = serialize(result)
    if action == "hint":
        session.status = "active"
    elif action == "escalation":
        session.status = "escalated"
    else:  # completed
        session.status = "completed"

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
        sources=[d.get("title", "") for d in (result.get("docs") or [])],
        agents=agent_io if settings.debug_agent_io else None,
    )
