"""Misconception Agent — categorizes the student's difficulty from the diagnostic Q&A.

Uses the probing questions and the student's answers (collected by the Diagnostic Agent)
to bucket the difficulty into ONE category. Does NOT teach.

Categories:
  * unsure_of_concept        — shaky / not sure about the concept itself
  * misunderstanding_concept — has an incorrect understanding of the concept
  * missing_prerequisite     — lacks a prerequisite the concept depends on
  * none                     — no clear difficulty
"""

from app.features.tutor.graph import llm

CATEGORIES = (
    "unsure_of_concept",
    "misunderstanding_concept",
    "missing_prerequisite",
    "none",
)

_SYSTEM = (
    "You are the Misconception Agent. Using the diagnostic probing Q&A and observations, "
    "classify the student's difficulty as EXACTLY one of these labels:\n"
    "  unsure_of_concept        - shaky/unsure about the concept itself\n"
    "  misunderstanding_concept - has a wrong understanding of the concept\n"
    "  missing_prerequisite     - lacks a prerequisite the concept depends on\n"
    "  none                     - no clear difficulty\n"
    "Reply with the label only — no explanation, no teaching."
)


async def misconception_node(state, config):
    diagnostic = state.get("diagnostic") or {}
    out = await llm.complete(
        "misconception",
        _SYSTEM,
        f"Concept: {state['concept']}\n"
        f"Observations: {diagnostic.get('observations')}\n"
        f"Probing Q&A: {diagnostic.get('qa')}",
    )
    label = out.strip().splitlines()[0].strip().lower()[:64] if out.strip() else "none"
    # Normalize to a known category when the model matches one; keep it lenient otherwise.
    if label not in CATEGORIES:
        label = next((c for c in CATEGORIES if c in label), label or "none")
    return {"misconception": label or "none"}
