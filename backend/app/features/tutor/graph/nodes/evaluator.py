"""Evaluator — checks the student's answer, records evidence, computes confidence.

On a wrong answer (with failures < 3 and no distress) it clears the plan/hint
so the supervisor loops back to the Planner for another attempt (section 2 of the guide).
"""

from app.features.tutor.graph import llm
from app.features.tutor.graph.prompts import evaluator as prompts
from app.features.tutor.graph.schemas import EvaluationResult
from app.features.tutor.models import EvidenceEvent
from app.features.tutor.repository import apply_evaluation


def _current_confidence(self_rating: int, correct: bool) -> float:
    # section 5: 0.4*self_rating + 0.3*correctness + 0.3*consistency
    self_rating_norm = (max(1, min(5, self_rating)) - 1) / 4
    correctness = 1.0 if correct else 0.0
    consistency = 1 - abs(self_rating_norm - correctness)
    return round(0.4 * self_rating_norm + 0.3 * correctness + 0.3 * consistency, 3)


async def evaluator_node(state, config):
    db = config["configurable"]["db"]
    student = config["configurable"]["student"]

    data = await llm.run_agent(
        "evaluator",
        EvaluationResult,
        prompts.SYSTEM,
        prompts.user(
            state["subject"],
            state["concept"],
            (state.get("tutor_plan") or {}).get("plan"),
            state["message"],
        ),
    )
    correct = bool(data.get("correct"))
    feedback = data.get("feedback", "")
    current_confidence = _current_confidence(state.get("self_rating", 3), correct)

    misconception = state.get("misconception")
    db.add(
        EvidenceEvent(
            student_id=student.id,
            session_id=state["session_id"],
            concept=state["concept"],
            correct=correct,
            error_type=None if correct else misconception,
        )
    )
    await db.flush()

    # Update the long-term profile on EVERY answer so the next session sees it.
    profile = await apply_evaluation(db, student.id, current_confidence, correct)

    updates: dict = {
        "evaluation": {
            "correct": correct,
            "feedback": feedback,
            "current_confidence": current_confidence,
        },
        "profile": profile,
        "is_answer": False,  # this answer is now consumed
    }

    if not correct:
        failures = state.get("failures", 0) + 1
        updates["failures"] = failures
        if failures < 3 and not state.get("distress"):
            # Loop back for another attempt with a more specific hint.
            updates.update(
                {
                    "tutor_plan": None,
                    "hint": None,
                    "hint_attempts": 0,
                    "evaluation": None,
                    "hint_level": state.get("hint_level", 1) + 1,
                    "last_feedback": feedback or "Not quite — let's try another angle.",
                }
            )
    return updates
