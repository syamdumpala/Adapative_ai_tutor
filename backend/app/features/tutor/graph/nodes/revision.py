"""Revision Planner — schedules the next review based on mastery (spaced repetition)."""

from datetime import UTC, datetime, timedelta

from app.features.tutor.repository import get_profile


async def revision_node(state, config):
    db = config["configurable"]["db"]
    student = config["configurable"]["student"]

    profile = await get_profile(db, student.id)
    mastery = profile.mastery if profile else 0.3
    days = 1 + round(mastery * 13)  # 1..14 days
    next_review = datetime.now(UTC) + timedelta(days=days)
    if profile is not None:
        profile.next_review = next_review
        await db.flush()

    output = state.get("output", "")
    output = f"{output} . Next review scheduled in {days} day(s)."
    return {"next_review": next_review.isoformat(), "action": "completed", "output": output}
