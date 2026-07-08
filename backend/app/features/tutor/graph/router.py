"""Supervisor routing — the conditional edges from the architecture guide (section 2).

if profile missing        -> profile
elif diagnostic missing   -> diagnostic
elif misconception missing-> misconception
elif tutor_plan missing   -> planner
elif docs missing         -> rag
elif hint missing         -> hint
elif evaluation missing   -> evaluator (only if the student has answered; else pause)
elif wrong and failures<3 -> planner   (evaluator normally clears fields itself)
elif failures>=3 / distress -> escalation
elif correct              -> memory
else                      -> await (END the turn)
"""

from app.features.tutor.graph.state import TutorState


def route(state: TutorState) -> str:
    if state.get("profile") is None:
        return "profile"
    if state.get("diagnostic") is None:
        return "diagnostic"
    if state.get("misconception") is None:
        return "misconception"
    if state.get("tutor_plan") is None:
        return "planner"
    if state.get("docs") is None:
        return "rag"
    if state.get("hint") is None:
        return "hint"

    evaluation = state.get("evaluation")
    if evaluation is None:
        if state.get("is_answer"):
            return "evaluator"
        return "await"  # hint delivered; wait for the student's answer

    if (
        evaluation.get("correct") is False
        and state.get("failures", 0) < 3
        and not state.get("distress")
    ):
        return "planner"  # safety net; evaluator usually clears fields to loop
    if state.get("failures", 0) >= 3 or state.get("distress"):
        return "escalation"
    if evaluation.get("correct") is True:
        return "memory"
    return "await"
