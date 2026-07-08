"""Tests for the multi-agent tutor graph.

The LLM is mocked at a single seam (`app.features.tutor.graph.llm.complete`), so no
real Claude call is made. The flow now begins with an interactive Diagnostic phase:
the tutor asks 3 probing questions (one per turn) before the first hint. The evaluator
mock treats any answer containing 'wrong' as incorrect.
"""

import json

import pytest

REGISTRATION = {
    "student_name": "Ada Lovelace",
    "student_id": "S001",
    "email": "ada@example.com",
    "password": "secret123",
}


async def _fake_complete(stage: str, system: str, user: str) -> str:
    if stage == "diagnostic":
        # The consolidate prompt asks to "summarize"; otherwise it's a probing question.
        if "summarize" in system.lower():
            return "The student is shaky on the prerequisite."
        return "What do you already know about this topic?"
    if stage == "misconception":
        return "missing_prerequisite"
    if stage == "planner":
        return "- Recall the definition\n- Work a small example"
    if stage == "hint":
        return "Think about what stays constant as the input changes."
    if stage == "guard":
        return "APPROVE"
    if stage == "evaluator":
        correct = "wrong" not in user.lower()
        return json.dumps(
            {"correct": correct, "feedback": "Nice work." if correct else "Not quite yet."}
        )
    return ""


@pytest.fixture
def mock_llm(monkeypatch):
    monkeypatch.setattr("app.features.tutor.routes.llm_is_configured", lambda: True)
    monkeypatch.setattr("app.features.tutor.graph.llm.complete", _fake_complete)


async def _auth_header(client):
    await client.post("/auth/register", json=REGISTRATION)
    login = await client.post(
        "/auth/login",
        json={"email": REGISTRATION["email"], "password": REGISTRATION["password"]},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


async def _ask(client, headers, question, session_id=None):
    body = {"question": question}
    if session_id:
        body["session_id"] = session_id
    return (await client.post("/tutor/ask", json=body, headers=headers)).json()


async def _reach_first_hint(client, headers):
    """Drive through the 3-question diagnostic phase; return (session_id, hint_response)."""
    first = await _ask(client, headers, "How do derivatives work?")
    assert first["action"] == "diagnostic"
    sid = first["session_id"]
    last = first
    for i in range(3):  # answer the 3 probing questions
        last = await _ask(client, headers, f"my answer {i}", sid)
    assert last["action"] == "hint"
    return sid, last


async def test_ask_requires_auth(client):
    resp = await client.post("/tutor/ask", json={"question": "Why is the sky blue?"})
    assert resp.status_code == 401


async def test_ask_without_llm_configured_returns_503(client, monkeypatch):
    monkeypatch.setattr("app.features.tutor.routes.llm_is_configured", lambda: False)
    headers = await _auth_header(client)
    resp = await client.post(
        "/tutor/ask", json={"question": "Why is the sky blue?"}, headers=headers
    )
    assert resp.status_code == 503


async def test_first_turn_asks_a_diagnostic_question(client, mock_llm):
    headers = await _auth_header(client)
    body = await _ask(client, headers, "How do derivatives work?")
    assert body["session_id"]
    assert body["action"] == "diagnostic"
    assert "Diagnostic 1/3" in body["message"]


async def test_diagnostic_phase_leads_to_hint(client, mock_llm):
    headers = await _auth_header(client)
    _, hint = await _reach_first_hint(client, headers)
    assert hint["action"] == "hint"
    assert "Hint" in hint["message"]
    assert hint["sources"]


async def test_correct_answer_completes(client, mock_llm):
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)
    body = await _ask(client, headers, "the answer is 42", sid)
    assert body["action"] == "completed"
    assert body["correct"] is True
    assert body["mastery"] is not None
    assert body["next_review"] is not None


async def test_repeated_wrong_answers_escalate(client, mock_llm):
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)
    last = None
    for _ in range(3):
        last = await _ask(client, headers, "this is wrong", sid)
    assert last["action"] == "escalation"


async def test_closed_session_conflicts(client, mock_llm):
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)
    await _ask(client, headers, "the answer is four", sid)  # completes it
    resp = await client.post(
        "/tutor/ask", json={"question": "again?", "session_id": sid}, headers=headers
    )
    assert resp.status_code == 409


async def test_unknown_session_returns_404(client, mock_llm):
    headers = await _auth_header(client)
    resp = await client.post(
        "/tutor/ask",
        json={"question": "hi", "session_id": "does-not-exist"},
        headers=headers,
    )
    assert resp.status_code == 404


async def test_ask_rejects_blank_question(client, mock_llm):
    headers = await _auth_header(client)
    resp = await client.post("/tutor/ask", json={"question": "   "}, headers=headers)
    assert resp.status_code == 422
