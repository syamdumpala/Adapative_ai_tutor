"""Diagnostic Agent — doctor-style probing.

Before any teaching, this agent asks the student ``DIAGNOSTIC_ROUNDS`` short probing
questions (ONE per turn) to gauge how well they know the concept behind their question
and its prerequisites. It records each answer, and once enough rounds are collected it
consolidates them into observations. The Misconception Agent then uses that Q&A to
categorize the student's difficulty.

It does NOT teach and does NOT give the answer.
"""

from app.features.tutor.graph import llm
from app.features.tutor.graph.prompts import diagnostic as prompts
from app.features.tutor.graph.schemas import DiagnosticObservations, DiagnosticQuestion

DIAGNOSTIC_ROUNDS = 3


def _qa_text(qa: list) -> str:
    return "\n".join(f"Q: {p['question']}\nA: {p['answer']}" for p in qa)


async def diagnostic_node(state, config):
    qa = list(state.get("diagnostic_qa") or [])
    pending = state.get("diagnostic_pending")
    profile = state.get("profile")
    asked = _qa_text(qa) or "(none yet)"
    subject = state.get("subject")

    # If this turn is the answer to the probing question we asked last turn, record it.
    if pending and state.get("incoming") == "diagnostic_answer":
        qa.append({"question": pending, "answer": state["message"]})
        pending = None

    # Enough probing rounds collected -> consolidate observations and move on.
    if len(qa) >= DIAGNOSTIC_ROUNDS:
        result = await llm.run_agent(
            "diagnostic",
            DiagnosticObservations,
            prompts.CONSOLIDATE_SYSTEM,
            prompts.consolidate_user(state["concept"], qa),
        )
        return {
            "diagnostic": {"observations": result["observations"], "qa": qa},
            "diagnostic_qa": qa,
            "diagnostic_pending": None,
        }

    # Otherwise ask the next probing question and pause for the student's answer.
    user_prompt = prompts.ask_user(
        subject, state["concept"], profile, asked, len(qa) + 1, DIAGNOSTIC_ROUNDS
    )
    result = await llm.run_agent("diagnostic", DiagnosticQuestion, prompts.ASK_SYSTEM, user_prompt)
    question = result["question"]
    return {
        "diagnostic_qa": qa,
        "diagnostic_pending": question,
        "diag_asked_this_turn": True,
        "action": "diagnostic",
        "output": f"(Diagnostic {len(qa) + 1}/{DIAGNOSTIC_ROUNDS}) {question}",
    }
