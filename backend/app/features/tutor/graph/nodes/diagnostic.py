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

_ASK_SYSTEM = (
    "You are the Diagnostic Agent of an adaptive tutor, working like a doctor who asks a "
    "few questions before diagnosing. Ask exactly ONE short probing question to check "
    "whether the student understands the concept behind their question and the "
    "prerequisites it depends on. Build on what they have already told you. "
    "Do NOT teach, do NOT reveal the answer, and ask only one question."
)

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
    asked = _qa_text(qa) or "(none yet)"
    question = await llm.complete(
        "diagnostic",
        _ASK_SYSTEM,
        f"Student's original question: {state['concept']}\n"
        f"Questions already asked and answered:\n{asked}\n"
        f"Now ask probing question #{len(qa) + 1} of {DIAGNOSTIC_ROUNDS}.",
    )
    return {
        "diagnostic_qa": qa,
        "diagnostic_pending": question,
        "diag_asked_this_turn": True,
        "action": "diagnostic",
        "output": f"(Diagnostic {len(qa) + 1}/{DIAGNOSTIC_ROUNDS}) {question}",
    }
