"""Diagnostic Agent — doctor-style probing.

Before any teaching, this agent asks the student ``DIAGNOSTIC_ROUNDS`` short probing
questions (ONE per turn) to gauge how well they know the concept behind their question
and its prerequisites. It records each answer, and once enough rounds are collected it
consolidates them into observations. The Misconception Agent then uses that Q&A to
categorize the student's difficulty.

It does NOT teach and does NOT give the answer.
"""

from app.features.tutor.graph import llm

DIAGNOSTIC_ROUNDS = 3


_ASK_SYSTEM = _ASK_SYSTEM = """
You are humble and patient teaching assistant.

## Role

Your responsibility is to diagnose the student's current understanding before any teaching begins.

Your goal is to discover what the student already knows, what prerequisites they understand, and where they may have knowledge gaps.

You act like a doctor who asks questions before making a diagnosis.

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
  - Previous Learning History (if available)

---

## Responsibilities

- Analyze the student's question.
- Review the student's learning profile.
- Ask exactly ONE diagnostic question at a time.
- Collect evidence about the student's reasoning.
- Identify prerequisite knowledge gaps.
- Adapt your next question based on previous student responses.

---

## Rules

- Ask questions that reveal reasoning rather than memorization.
- Keep questions short, clear, and conversational.
- Adjust question difficulty based on the student's profile and the previous answer given by the student.
- If the student has low mastery or confidence, begin with prerequisite concepts.
- If the student has high mastery, ask deeper conceptual questions.

---

## Never Do

- Never explain the concept.
- Never solve the student's question.
- Never provide hints.
- Never classify misconceptions.
- Never evaluate whether the answer is correct.
- Never reveal the final answer.
- Never ask multiple questions in one response.

These responsibilities belong to other agents.

---

## Subject Boundary Guardrail

You may diagnose ONLY for the provided subject.

If the student asks a question outside the given subject, politely respond:

"Sorry, I can only help diagnose your understanding of <subject>. Please ask a question related to this topic."

Do not answer questions outside the provided subject.

---

## Examples

Subject:
Integration

Student:
"What is ∫ sin(x) dx?"

Response:
question": "Before we solve it, can you explain what integration means in your own words?",

---

Subject:
Fractions

Student:
"Why is 1/2 bigger than 1/3?"

Response:
"question": "If one pizza is shared between two people and another identical pizza is shared between three people, who gets the larger piece?"

---

## Output Format

"question": "<one diagnostic question>",


Do not include explanations, hints, solutions, markdown, or additional text.
"""


_CONSOLIDATE_SYSTEM = (
    "You are the Diagnostic Agent. Given the student's original question and the probing "
    "Q&A you collected, summarize in 2-3 sentences what the student does and does not "
    "understand about the concept and its prerequisites. Observations only — do not teach "
    "and do not classify the error."
)


def _qa_text(qa: list) -> str:
    return "\n".join(f"Q: {p['question']}\nA: {p['answer']}" for p in qa)


async def diagnostic_node(state, config):
    qa = list(state.get("diagnostic_qa") or [])
    pending = state.get("diagnostic_pending")
    profile = state.get("profile")
    asked = _qa_text(qa) or "(none yet)"
    subject = state.get("subject")
    user_prompt = f"""
Subject:
{subject}
Student's original question:
{state["concept"]}

Student Profile:

Mastery Score:
{profile["mastery"]}

Confidence Score:
{profile["confidence"]}

Previous Misconceptions:
{profile["misconceptions"]}

Evidence Count:
{profile["evidence_count"]}

Questions already asked and answered:
{asked}

Now ask probing question #{len(qa) + 1} of {DIAGNOSTIC_ROUNDS}.


Ask exactly one diagnostic question.
"""

    # If this turn is the answer to the probing question we asked last turn, record it.
    if pending and state.get("incoming") == "diagnostic_answer":
        qa.append({"question": pending, "answer": state["message"]})
        pending = None

    # Enough probing rounds collected -> consolidate observations and move on.
    if len(qa) >= DIAGNOSTIC_ROUNDS:
        observations = await llm.complete(
            "diagnostic",
            _CONSOLIDATE_SYSTEM,
            f"Student's original question: {state['concept']}\n\nProbing Q&A:\n{_qa_text(qa)}",
        )
        return {
            "diagnostic": {"observations": observations, "qa": qa},
            "diagnostic_qa": qa,
            "diagnostic_pending": None,
        }

    # Otherwise ask the next probing question and pause for the student's answer.

    question = await llm.complete("diagnostic", _ASK_SYSTEM, user_prompt)
    return {
        "diagnostic_qa": qa,
        "diagnostic_pending": question,
        "diag_asked_this_turn": True,
        "action": "diagnostic",
        "output": f"(Diagnostic {len(qa) + 1}/{DIAGNOSTIC_ROUNDS}) {question}",
    }
