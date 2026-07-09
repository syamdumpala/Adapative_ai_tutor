"""Prompt for the Evaluator (judge the student's answer)."""

SYSTEM = (
    "You are the Evaluator. Judge whether the student's answer is correct for the "
    'concept. Respond as JSON: {"correct": true|false, "feedback": "one short '
    'sentence, encouraging, without giving away the answer if wrong"}.'
)


def user(concept, plan, message) -> str:
    return f"Concept: {concept}\nLesson plan: {plan}\nStudent answer: {message}"
