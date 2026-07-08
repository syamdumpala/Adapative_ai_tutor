"""Diagnostic Agent — probes the student's understanding and records observations.

Does NOT classify the error (that is the Misconception Agent's job).
"""

from app.features.tutor.graph import llm

_SYSTEM = (
    "You are the Diagnostic Agent of an adaptive tutor. Given the concept and the "
    "student's message, briefly note what the student seems to understand and where "
    "they may be struggling. Output 1-2 sentences of observations only. Do not teach, "
    "do not give the answer, do not classify the error type."
)


async def diagnostic_node(state, config):
    observations = await llm.complete(
        "diagnostic",
        _SYSTEM,
        f"Concept: {state['concept']}\nStudent message: {state['message']}\n"
        f"Profile: {state.get('profile')}",
    )
    return {"diagnostic": {"observations": observations}}
