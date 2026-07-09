"""Supervisor routing — the conditional edges from the architecture guide (section 2).

if profile missing        -> profile
elif diagnostic missing   -> diagnostic
elif misconception missing-> misconception
elif tutor_plan missing   -> planner
elif hint missing         -> hint
elif evaluation missing   -> evaluator (only if the student has answered; else pause)
elif distress             -> escalation
elif wrong (no distress)  -> planner   (evaluator normally clears fields itself)
elif correct              -> memory
else                      -> await (END the turn)

Hints are unlimited — there is no failure cap; only distress escalates to a teacher.
"""

from app.features.tutor.graph.state import TutorState


def route(state: TutorState) -> str:
    if state.get("profile") is None:
        return "profile"
    if state.get("diagnostic") is None:
        # Interactive diagnostic phase: ask DIAGNOSTIC_ROUNDS probing questions, one per
        # turn. If we asked one this turn, pause (END) for the student's answer; otherwise
        # run the diagnostic node to record an answer and ask the next / consolidate.
        if state.get("diag_asked_this_turn"):
            return "await"
        return "diagnostic"
    if state.get("misconception") is None:
        return "misconception"
    if state.get("tutor_plan") is None:
        return "planner"
    if state.get("hint") is None:
        return "hint"

    evaluation = state.get("evaluation")
    if evaluation is None:
        if state.get("is_answer"):
            return "evaluator"
        return "await"  # hint delivered; wait for the student's answer

    if state.get("distress"):
        return "escalation"  # only distress ends the loop — hints are unlimited
    if evaluation.get("correct") is False:
        return "planner"  # safety net; evaluator usually clears fields to loop
    if evaluation.get("correct") is True:
        return "memory"
    return "await"
