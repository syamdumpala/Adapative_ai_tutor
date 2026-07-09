"""Profile Agent — loads (or creates) the student's long-term profile."""

from app.features.tutor.repository import get_or_create_profile


async def profile_node(state, config):
    db = config["configurable"]["db"]
    student = config["configurable"]["student"]
    profile = await get_or_create_profile(db, student.id)
    return {
        "profile": {
            "mastery": profile.mastery,
            "confidence": profile.confidence,
            "misconceptions": profile.misconceptions or [],
            "evidence_count": profile.evidence_count or 0,
        }
    }
