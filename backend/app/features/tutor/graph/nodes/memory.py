"""Memory Agent — finalizes a correct answer.

Long-term profile saving (mastery, confidence, misconceptions, evidence_count) now
happens in the Evaluator on EVERY answer via `apply_evaluation`, so it persists even
when a student never reaches a correct answer. This node just reads the already-updated
profile from state and produces the success message.
"""

from app.features.tutor.repository import get_session, record_session_analytics


async def memory_node(state, config):
    db = config["configurable"]["db"]
    student = config["configurable"]["student"]
    profile = state.get("profile") or {}
    feedback = state["evaluation"].get("feedback", "")
    mastery = profile.get("mastery")

    # Reaching this node means the concept is mastered (history mode): snapshot the
    # learning analytics (subject vs mastery vs confidence) for the charts.
    session = await get_session(db, state["session_id"], student.id)
    if session is not None:
        await record_session_analytics(db, session, state)

    return {
        "action": "completed",
        "output": f"{feedback} . Great — you've got it! Mastery is now {mastery}.",
    }
