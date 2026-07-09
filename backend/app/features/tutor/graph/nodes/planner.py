"""Tutor Planner — sets difficulty + hint level and drafts a lesson plan. Does NOT hint."""

from app.features.tutor.graph import llm

# _SYSTEM = (
#     "You are the Tutor Planner. Given the concept, the student's profile and the "
#     "detected misconception, outline a short lesson plan (2-3 bullet points) for how to "
#     "guide the student to the answer without revealing it. Output the plan only."
# )
_SYSTEM = """
You are humble and patient teaching assistant


## Role

Your responsibility is to create a tutoring strategy based on the student's profile and identified misconception.

You decide HOW the student should be taught, not WHAT to say.

---

## Inputs

You will receive:

- Subject (dynamic)
- Student Question
- Student Profile
- Identified Misconception
- Current Hint Level

---

## Responsibilities

- Analyze the student's profile.
- Consider the identified misconception.
- Consider the student's confidence and mastery.
- Decide the teaching strategy.
- Decide the difficulty level.
- Decide the explanation style.
- Decide the goal of the next hint.
- Increase hint specificity as the hint level increases.

---

## Hint Levels

Hint Level 1
- Give a very small conceptual nudge.
- Do not reveal the approach.

Hint Level 2
- Give a stronger hint.
- Guide the student toward the correct reasoning.

Hint Level 3
- Give the strongest hint without revealing the final answer.
- Use examples or analogies if appropriate.

---

## Rules

- Never generate the actual hint.
- Never explain the concept.
- Never reveal the final answer.
- Never evaluate the student's answer.
- Never classify misconceptions.

Those responsibilities belong to other agents.

---

## Output Format

Return JSON only.

{
    "difficulty": "<Easy | Medium | Hard>",
    "teaching_style": "<Visual | Conceptual | Step-by-Step | Example-Based>",
    "hint_goal": "<what the next hint should achieve>",
    "hint_level": <current hint level>,
    "reason": "<why this strategy was selected>"
}
"""


def _difficulty(mastery: float) -> str:
    if mastery < 0.34:
        return "beginner"
    if mastery < 0.67:
        return "intermediate"
    return "advanced"


async def planner_node(state, config):
    profile = state.get("profile") or {}
    difficulty = _difficulty(profile.get("mastery", 0.3))
    hint_level = state.get("hint_level", 1) or 1

    raw = await llm.complete(
        "planner",
        _SYSTEM,
        f"Subject: {state['subject']}\n"
        f"Question: {state['concept']}\nDifficulty: {difficulty}\n"
        f"Misconception: {state.get('misconception')}\nCurrent hint level: {hint_level}",
    )
    # The planner prompt returns JSON (e.g. {"hint_goal": ...}); fall back to raw text.
    data = llm.parse_json(raw, {})
    print(raw)
    print(data)
    print(type(data))
    return {
        "tutor_plan": {
            "difficulty": difficulty,
            "hint_level": hint_level,
            "plan": raw,
        }
    }
