"""Hint Agent — generates Hint 1/2/3 based on the plan.

Must NOT reveal the final answer. Output is validated by the Hint Guard next.
"""

from app.features.tutor.graph import llm
from app.features.tutor.graph.prompts import hint as prompts
from app.features.tutor.graph.schemas import HintResult


async def hint_node(state, config):
    level = state.get("hint_level", 1)
    plan = state.get("tutor_plan") or {}
    hint = state.get("hint") or ""
    # Student confidence (0..1) tunes hint difficulty: low → easier, high → tougher.
    confidence = (state.get("profile") or {}).get("confidence")
    result = await llm.run_agent(
        "hint",
        HintResult,
        prompts.SYSTEM,
        prompts.user(state.get("subject"), state["concept"], plan, level, confidence, hint),
        history=config["configurable"].get("history"),
        subject=state.get("subject"),
    )
    return {"hint": result["hint"]}
