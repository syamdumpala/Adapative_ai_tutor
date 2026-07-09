"""Hint Guard — validates the hint. Approves it or sends it back to be regenerated.

Does NOT create hints itself. Caps regeneration attempts to avoid loops.
"""

from app.features.tutor.graph import llm
from app.features.tutor.graph.prompts import guard as prompts
from app.features.tutor.graph.schemas import GuardResult

_MAX_ATTEMPTS = 2


async def guard_node(state, config):
    result = await llm.run_agent(
        "guard",
        GuardResult,
        prompts.SYSTEM,
        prompts.user(state["concept"], state.get("hint")),
    )
    approved = not str(result["verdict"]).strip().upper().startswith("REJECT")
    attempts = state.get("hint_attempts", 0)

    if approved or attempts + 1 >= _MAX_ATTEMPTS:
        level = state.get("hint_level", 1)
        feedback = state.get("last_feedback")
        prefix = f"{feedback}\n\n" if feedback else ""
        output = f"{prefix}Hint {level}: {state.get('hint')}"
        return {
            "hint_approved": True,
            "action": "hint",
            "output": output,
            "last_feedback": None,
        }

    # Rejected — clear the hint so the supervisor routes back to the Hint Agent.
    return {"hint": None, "hint_attempts": attempts + 1, "hint_approved": False}
