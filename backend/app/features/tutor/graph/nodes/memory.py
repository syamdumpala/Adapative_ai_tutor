"""Memory Agent — saves long-term learning after a correct answer. Does NOT evaluate.

Applies the memory rules (section 7): a misconception is only stored once it has
>= 2 pieces of evidence across questions.
"""

from app.features.tutor.repository import consolidate_misconceptions, get_profile


async def memory_node(state, config):
    db = config["configurable"]["db"]
    student = config["configurable"]["student"]

    profile = await get_profile(db, student.id)
    if profile is None:
        return {"output": state.get("output", ""), "action": "completed"}

    current = state["evaluation"]["current_confidence"]
    # section 5: long-term confidence = 0.8*old + 0.2*current
    profile.confidence = round(0.8 * profile.confidence + 0.2 * current, 3)
    profile.mastery = round(min(1.0, 0.8 * profile.mastery + 0.2 * 1.0), 3)
    profile.evidence_count = (profile.evidence_count or 0) + 1
    profile.misconceptions = await consolidate_misconceptions(db, student.id)
    await db.flush()

    feedback = state["evaluation"].get("feedback", "")
    return {
        "profile": {
            "mastery": profile.mastery,
            "confidence": profile.confidence,
            "misconceptions": profile.misconceptions,
            "evidence_count": profile.evidence_count,
        },
        "action": "completed",
        "output": f"{feedback}\n\nGreat — you've got it! Mastery is now {profile.mastery}.",
    }
