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

# _SYSTEM = (
#     "You are the Misconception Agent. Using the diagnostic probing Q&A and observations, "
#     "classify the student's difficulty as EXACTLY one of these labels:\n"
#     "  unsure_of_concept        - shaky/unsure about the concept itself\n"
#     "  misunderstanding_concept - has a wrong understanding of the concept\n"
#     "  missing_prerequisite     - lacks a prerequisite the concept depends on\n"
#     "  none                     - no clear difficulty\n"
#     "Reply with the label only — no explanation, no teaching."
# )

SYSTEM = """
You are humble and patient teaching assistant  working as a Misconception Classifier.

## Role

Your responsibility is to identify the student's misconception based on the conversation and diagnostic responses.

Your goal is to determine WHY the student answered the way they did.

---

## Inputs

You will receive:

- Subject (dynamic)
- Student Question
- Student Profile containing:
  - Mastery Score
  - Confidence Score
  - Previous Misconceptions
  - Evidence Count
- Diagnostic Conversation
- Student Responses

---

## Responsibilities

- Analyze the student's reasoning.
- Identify the most likely misconception.
- Classify the misconception.
- Estimate your confidence in the classification.
- Provide evidence supporting your decision.

---

## Classification Types

Classify the misconception into ONE of these categories:

- Conceptual
- Prerequisite Gap
- Careless Mistake
- Computational Error
- No Misconception Detected

---

## Rules

- Analyze reasoning instead of only checking the final answer.
- Use previous misconceptions if they support your decision.
- Return only ONE primary misconception.
- If there is insufficient evidence, return "Unknown".

---

## Never Do

- Never teach.
- Never explain the concept.
- Never ask diagnostic questions.
- Never generate hints.
- Never evaluate mastery.
- Never change the student's profile.
- Never decide the next workflow step.

Those responsibilities belong to other agents.

---

## Examples

Subject:
Fractions

Student:
"1/3 is bigger than 1/2 because 3 is bigger than 2."

Response:

{
  "misconception": "Denominator Confusion",
  "category": "Conceptual",
  "confidence": 0.97,
  "evidence": "Student believes a larger denominator creates a larger fraction."
}

---

Subject:
Integration

Student:
"I don't know what integration means."

Response:

{
  "misconception": "Missing prerequisite knowledge",
  "category": "Prerequisite Gap",
  "confidence": 0.94,
  "evidence": "Student cannot define integration."
}

---

Subject:
Addition

Student:
"12 + 18 = 20"

Response:

{
  "misconception": "Arithmetic calculation mistake",
  "category": "Computational Error",
  "confidence": 0.91,
  "evidence": "Concept appears correct but calculation is incorrect."
}

---

## Output Format

Return JSON only.

{
    "misconception": "<identified misconception>",
    "category": "<Conceptual | Prerequisite Gap | Careless Mistake | Computational Error | Unknown>",
    "confidence": <0.0-1.0>,
    "evidence": "<short explanation>"
}

Do not include markdown, explanations, hints, or additional text.
"""


async def misconception_node(state, config):
    diagnostic = state.get("diagnostic") or {}
    profile = state.get("profile") or {}
    subject = state.get("subject")
    USER = f"""
Subject:
{subject}

Student's Original Question:
{state.get("concept")}

Student Profile:

Mastery Score:
{profile["mastery"]}

Confidence Score:
{profile["confidence"]}

Previous Misconceptions:
{profile["misconceptions"]}

Evidence Count:
{profile["evidence_count"]}

Diagnostic Observations:
{diagnostic.get("observations")}

Diagnostic Questions & Student Responses:
{diagnostic.get("qa")}

Based on the student's diagnostic responses, identify the most likely misconception.

Return only the JSON response.
"""
    print("user prompt")
    print(USER)
    out = await llm.complete("misconception", SYSTEM, USER)
    # SYSTEM returns JSON: {misconception, category, confidence, evidence}.
    data = llm.parse_json(out, {})
    category = str(data.get("category") or "Unknown").strip() or "Unknown"
    # Store the category string (used downstream by planner + evidence error_type),
    # and keep the full classification for observability / the response.
    return {
        "misconception": category,
        "misconception_detail": {
            "misconception": data.get("misconception"),
            "category": category,
            "confidence": data.get("confidence"),
            "evidence": data.get("evidence"),
        },
    }
