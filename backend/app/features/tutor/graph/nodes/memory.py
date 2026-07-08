"""Memory Agent — finalizes a correct answer.

Long-term profile saving (mastery, confidence, misconceptions, evidence_count) now
happens in the Evaluator on EVERY answer via `apply_evaluation`, so it persists even
when a student never reaches a correct answer. This node just reads the already-updated
profile from state and produces the success message.
"""


async def memory_node(state, config):
    profile = state.get("profile") or {}
    feedback = state["evaluation"].get("feedback", "")
    mastery = profile.get("mastery")
    return {
        "action": "completed",
        "output": f"{feedback}\n\nGreat — you've got it! Mastery is now {mastery}.",
    }
