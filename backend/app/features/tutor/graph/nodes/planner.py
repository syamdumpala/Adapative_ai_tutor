"""Tutor Planner — sets difficulty + hint level and drafts a lesson plan. Does NOT hint."""

from app.features.tutor.graph import llm

_SYSTEM = (
    "You are the Tutor Planner. Given the concept, the student's profile and the "
    "detected misconception, outline a short lesson plan (2-3 bullet points) for how to "
    "guide the student to the answer without revealing it. Output the plan only."
)


def _difficulty(mastery: float) -> str:
    if mastery < 0.34:
        return "beginner"
    if mastery < 0.67:
        return "intermediate"
    return "advanced"


async def planner_node(state, config):
    profile = state.get("profile") or {}
    difficulty = _difficulty(profile.get("mastery", 0.3))
    hint_level = state.get("hint_level", 1) or 1

    plan_text = await llm.complete(
        "planner",
        _SYSTEM,
        f"Concept: {state['concept']}\nDifficulty: {difficulty}\n"
        f"Misconception: {state.get('misconception')}\nCurrent hint level: {hint_level}",
    )
    return {
        "tutor_plan": {
            "difficulty": difficulty,
            "hint_level": hint_level,
            "plan": plan_text,
        }
    }
