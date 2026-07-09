"""Escalation Agent — hands off to a human teacher on repeated failure or distress."""

from app.features.tutor.models import TeacherEscalation


async def escalation_node(state, config):
    db = config["configurable"]["db"]
    student = config["configurable"]["student"]

    reason = "Student distress detected"
    db.add(
        TeacherEscalation(
            student_id=student.id,
            session_id=state["session_id"],
            reason=reason,
        )
    )
    await db.flush()

    return {
        "escalation": {"reason": reason},
        "action": "escalation",
        "output": (
            "I've asked a human teacher to step in and help you with this — "
            f"they'll follow up soon. ({reason})"
        ),
    }
