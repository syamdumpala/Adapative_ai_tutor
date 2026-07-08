"""Hint Agent — generates Hint 1/2/3 based on the plan and retrieved docs.

Must NOT reveal the final answer. Output is validated by the Hint Guard next.
"""

from app.features.tutor.graph import llm

_SYSTEM = (
    "You are the Hint Agent of an adaptive tutor. Produce ONE progressive hint at the "
    "requested level (higher level = more specific), guiding the student toward the "
    "answer. NEVER state the final answer outright. Keep it to 1-3 sentences."
)


async def hint_node(state, config):
    level = state.get("hint_level", 1)
    plan = state.get("tutor_plan") or {}
    docs_text = "\n".join(d.get("content", "") for d in (state.get("docs") or []))
    hint = await llm.complete(
        "hint",
        _SYSTEM,
        f"Concept: {state['concept']}\nHint level: {level}\n"
        f"Lesson plan: {plan.get('plan')}\nReference material: {docs_text}\n"
        "Remember: do not reveal the final answer.",
    )
    return {"hint": hint}
