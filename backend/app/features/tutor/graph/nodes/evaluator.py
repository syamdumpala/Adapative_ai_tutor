"""Evaluator — checks the student's answer, records evidence, computes confidence.

On a wrong answer (and no distress) it clears the plan/hint so the supervisor loops back
to the Planner for another attempt. Hints are unlimited: only distress ends the loop.
"""

from app.features.tutor.graph import llm
from app.features.tutor.graph.prompts import evaluator as prompts
from app.features.tutor.graph.schemas import EvaluationResult
from app.features.tutor.models import EvidenceEvent
from app.features.tutor.repository import apply_concept_evaluation, apply_evaluation


def _current_confidence(self_rating: int, correct: bool) -> float:
    # section 5: 0.4*self_rating + 0.3*correctness + 0.3*consistency
    self_rating_norm = (max(1, min(5, self_rating)) - 1) / 4
    correctness = 1.0 if correct else 0.0
    consistency = 1 - abs(self_rating_norm - correctness)
    return round(0.4 * self_rating_norm + 0.3 * correctness + 0.3 * consistency, 3)


async def evaluator_node(state, config):
    db = config["configurable"]["db"]
    student = config["configurable"]["student"]

    # The evaluator judges the student's answer against the INITIAL question
    # (`state["concept"]`). The full session transcript (history) is prepended so it can
    # see every hint given and decide whether the answer solves that initial question.
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
        history=config["configurable"].get("history"),
        subject=state["subject"],
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

    # Mirror that update onto the per-concept state (the grain the By-topic charts read),
    # so live tutoring — not just the seed — moves the student's topic mastery.
    concept_id = state.get("concept_id")
    if concept_id:
        await apply_concept_evaluation(db, student.id, concept_id, current_confidence, correct)

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
        # Unlimited hints: on every wrong answer we loop back for a fresh, more specific
        # hint. Only student distress ends the loop (-> escalation); there is no attempt cap.
        if not state.get("distress"):
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
