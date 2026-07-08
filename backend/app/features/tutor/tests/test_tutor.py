"""Tests for the multi-agent tutor graph.

The LLM is mocked at a single seam (`app.features.tutor.graph.llm.complete`), so
no real Claude call is made. The evaluator's mock treats any answer containing the
word 'wrong' as incorrect, which lets tests drive the correct / retry / escalate paths.
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
        return "The student is unsure about the core idea."
    if stage == "misconception":
        return "none"
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
    # Treat the LLM as configured (provider-agnostic) and stub the completion seam.
    monkeypatch.setattr("app.features.tutor.routes.llm_is_configured", lambda: True)
    monkeypatch.setattr("app.features.tutor.graph.llm.complete", _fake_complete)


async def _auth_header(client):
    await client.post("/auth/register", json=REGISTRATION)
    login = await client.post(
        "/auth/login",
        json={"email": REGISTRATION["email"], "password": REGISTRATION["password"]},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


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


async def test_first_turn_returns_hint(client, mock_llm):
    headers = await _auth_header(client)
    resp = await client.post(
        "/tutor/ask", json={"question": "How do derivatives work?"}, headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"]
    assert body["action"] == "hint"
    assert "Hint" in body["message"]
    assert body["sources"]  # RAG stub attaches a source


async def test_correct_answer_completes(client, mock_llm):
    headers = await _auth_header(client)
    turn1 = (
        await client.post("/tutor/ask", json={"question": "What is 6 x 7?"}, headers=headers)
    ).json()
    sid = turn1["session_id"]

    turn2 = await client.post(
        "/tutor/ask",
        json={"question": "the answer is 42", "session_id": sid, "self_rating": 4},
        headers=headers,
    )
    assert turn2.status_code == 200
    body = turn2.json()
    assert body["action"] == "completed"
    assert body["correct"] is True
    assert body["mastery"] is not None
    assert body["next_review"] is not None


async def test_repeated_wrong_answers_escalate(client, mock_llm):
    headers = await _auth_header(client)
    sid = (
        await client.post("/tutor/ask", json={"question": "Integrate x^2"}, headers=headers)
    ).json()["session_id"]

    last = None
    for _ in range(3):
        last = await client.post(
            "/tutor/ask",
            json={"question": "this is wrong", "session_id": sid},
            headers=headers,
        )
        assert last.status_code == 200

    assert last.json()["action"] == "escalation"


async def test_closed_session_conflicts(client, mock_llm):
    headers = await _auth_header(client)
    sid = (
        await client.post("/tutor/ask", json={"question": "What is 2+2?"}, headers=headers)
    ).json()["session_id"]
    # Finish the session correctly.
    await client.post(
        "/tutor/ask",
        json={"question": "the answer is four", "session_id": sid},
        headers=headers,
    )
    # Any further message on the closed session is a conflict.
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
