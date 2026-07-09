"""Tests for the multi-agent tutor graph.

The agents are mocked at a single seam (`app.features.tutor.graph.llm.run_agent`), so
no real Claude call is made. Each agent returns a dict matching its JSON response
schema. The flow begins with an interactive Diagnostic phase: the tutor asks 3 probing
questions (one per turn) before the first hint. The evaluator mock treats any answer
containing 'wrong' as incorrect.
"""

import pytest

REGISTRATION = {
    "student_name": "Ada Lovelace",
    "student_id": "S001",
    "email": "ada@example.com",
    "password": "secret123",
}


async def _fake_run_agent(
    stage: str, schema, system: str, user: str, history=None, subject=None
) -> dict:
    if stage == "diagnostic":
        # The consolidate prompt asks to "summarize"; otherwise it's a probing question.
        if "summarize" in system.lower():
            return {"observations": "The student is shaky on the prerequisite."}
        return {"question": "What do you already know about this topic?"}
    if stage == "misconception":
        return {
            "misconception": "Missing prerequisite knowledge",
            "category": "missing_prerequisite",
            "confidence": 0.9,
            "evidence": "Student cannot recall the definition.",
        }
    if stage == "planner":
        return {
            "difficulty": "Easy",
            "teaching_style": "Conceptual",
            "hint_goal": "Recall the definition",
            "hint_level": 1,
            "reason": "Low mastery on the prerequisite.",
        }
    if stage == "hint":
        return {"hint": "Think about what stays constant as the input changes."}
    if stage == "guard":
        return {"verdict": "APPROVE"}
    if stage == "evaluator":
        correct = "wrong" not in user.lower()
        return {"correct": correct, "feedback": "Nice work." if correct else "Not quite yet."}
    return {}


@pytest.fixture
def mock_llm(monkeypatch):
    monkeypatch.setattr("app.features.tutor.routes.llm_is_configured", lambda: True)
    monkeypatch.setattr("app.features.tutor.graph.llm.run_agent", _fake_run_agent)


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


async def test_correct_answer_completes(client, mock_llm):
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)
    body = await _ask(client, headers, "the answer is 42", sid)
    assert body["action"] == "completed"
    assert body["correct"] is True
    assert body["mastery"] is not None
    assert body["next_review"] is not None


async def test_unlimited_hints_no_escalation_on_repeated_wrong(client, mock_llm):
    # Hints are unlimited now: repeated wrong answers keep producing new hints and never
    # auto-escalate.
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)
    last = None
    for _ in range(5):
        last = await _ask(client, headers, "this is wrong", sid)
        assert last["action"] == "hint"
    assert last["action"] == "hint"


async def test_distress_escalates(client, mock_llm):
    # Only student distress ends the loop (hands off to a teacher).
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)
    body = await _ask(client, headers, "i give up, this is too hard", sid)
    assert body["action"] == "escalation"


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


async def test_conversation_api_returns_full_transcript(client, mock_llm):
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)

    resp = await client.get(f"/tutor/sessions/{sid}/conversation", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["session_id"] == sid
    assert body["initial_question"] == "How do derivatives work?"

    kinds = [m["kind"] for m in body["messages"]]
    roles = [m["role"] for m in body["messages"]]
    # The very first message is the student's initial question, and the transcript
    # includes diagnostic questions/answers and at least one hint.
    assert body["messages"][0]["role"] == "student"
    assert body["messages"][0]["kind"] == "question"
    assert "diagnostic_question" in kinds
    assert "diagnostic_answer" in kinds
    assert "hint" in kinds
    assert set(roles) <= {"student", "tutor"}


async def test_sessions_list_and_conversation_isolation(client, mock_llm):
    headers = await _auth_header(client)
    sid, _ = await _reach_first_hint(client, headers)

    # /tutor/sessions returns the paginated chat rail (Page envelope); the newly
    # created session must appear in it.
    sessions = (await client.get("/tutor/sessions", headers=headers)).json()
    assert any(s["id"] == sid for s in sessions["items"])

    # A conversation for an unknown session is a 404.
    missing = await client.get("/tutor/sessions/nope/conversation", headers=headers)
    assert missing.status_code == 404
