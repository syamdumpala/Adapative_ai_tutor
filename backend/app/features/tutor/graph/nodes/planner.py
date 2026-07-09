"""Tutor Planner — sets difficulty + hint level and drafts a lesson plan. Does NOT hint."""

from app.features.tutor.graph import llm
from app.features.tutor.graph.prompts import planner as prompts
from app.features.tutor.graph.schemas import PlannerResult


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

    plan = await llm.run_agent(
        "planner",
        PlannerResult,
        prompts.SYSTEM,
        prompts.user(
            state["subject"], state["concept"], difficulty, state.get("misconception"), hint_level
        ),
    )
    return {
        "tutor_plan": {
            "difficulty": difficulty,
            "hint_level": hint_level,
            "plan": plan,
        }
    }
