"""Misconception Agent — categorizes the student's difficulty from the diagnostic Q&A.

Uses the probing questions and the student's answers (collected by the Diagnostic Agent)
to bucket the difficulty into ONE category. Does NOT teach.
"""

from app.features.tutor.graph import llm
from app.features.tutor.graph.prompts import misconception as prompts
from app.features.tutor.graph.schemas import MisconceptionResult


async def misconception_node(state, config):
    diagnostic = state.get("diagnostic") or {}
    profile = state.get("profile") or {}
    subject = state.get("subject")

    data = await llm.run_agent(
        "misconception",
        MisconceptionResult,
        prompts.SYSTEM,
        prompts.user(subject, state.get("concept"), profile, diagnostic),
    )
    category = str(data.get("category") or "Unknown").strip() or "Unknown"
    # Store the category string (used downstream by planner + evidence error_type),
    # and keep the full classification for observability / the response.
    return {
        "misconception": category,
        "misconception_detail": {
            "misconception": data.get("misconception"),
            "category": category,
            "confidence": data.get("confidence"),
            "evidence": data.get("evidence"),
        },
    }
