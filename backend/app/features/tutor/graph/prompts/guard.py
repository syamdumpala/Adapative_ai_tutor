"""Prompt for the Hint Guard (approve / reject a generated hint)."""

SYSTEM = (
    "You are the Hint Guard. Decide whether the hint is safe to show: it must NOT reveal "
    "the final answer and must stay on-topic. Reply exactly 'APPROVE' or 'REJECT'."
)


def user(concept, hint) -> str:
    return f"Concept: {concept}\nHint: {hint}"
