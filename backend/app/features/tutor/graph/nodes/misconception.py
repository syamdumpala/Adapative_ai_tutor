"""Misconception Agent — classifies the likely error type. Does NOT teach."""

from app.features.tutor.graph import llm

_SYSTEM = (
    "You are the Misconception Agent. From the diagnostic observations, classify the "
    "student's likely misconception as a short snake_case label (e.g. sign_error, "
    "off_by_one, confuses_area_perimeter). If there is no clear misconception, reply "
    "exactly 'none'. Reply with the label only — no explanation, no teaching."
)


async def misconception_node(state, config):
    out = await llm.complete(
        "misconception",
        _SYSTEM,
        f"Concept: {state['concept']}\nObservations: {state.get('diagnostic')}",
    )
    label = out.strip().splitlines()[0].strip().lower()[:128] if out.strip() else "none"
    return {"misconception": label or "none"}
