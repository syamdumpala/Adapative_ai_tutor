"""Hint Guard — validates the hint. Approves it or sends it back to be regenerated.

Does NOT create hints itself. Caps regeneration attempts to avoid loops.
"""

from app.features.tutor.graph import llm

_SYSTEM = (
    "You are the Hint Guard. Decide whether the hint is safe to show: it must NOT reveal "
    "the final answer and must stay on-topic. Reply exactly 'APPROVE' or 'REJECT'."
)

_MAX_ATTEMPTS = 2


async def guard_node(state, config):
    verdict = await llm.complete(
        "guard",
        _SYSTEM,
        f"Concept: {state['concept']}\nHint: {state.get('hint')}",
    )
    approved = not verdict.strip().upper().startswith("REJECT")
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
