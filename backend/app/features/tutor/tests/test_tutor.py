"""Unit / API tests for the tutor feature.

The LangGraph pipeline is monkeypatched so tests never call Claude.
"""

from app.core.config import settings

REGISTRATION = {
    "student_name": "Ada Lovelace",
    "student_id": "S001",
    "email": "ada@example.com",
    "password": "secret123",
}


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


async def test_ask_without_api_key_returns_503(client, monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", None)
    headers = await _auth_header(client)
    resp = await client.post(
        "/tutor/ask", json={"question": "Why is the sky blue?"}, headers=headers
    )
    assert resp.status_code == 503


async def test_ask_with_mocked_pipeline(client, monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")

    async def fake_pipeline(question: str, student_name: str) -> dict:
        return {
            "analysis": "Physics question, beginner level.",
            "answer": "Rayleigh scattering makes the sky blue.",
            "followups": ["What is scattering?", "Why is sunset red?", "What is a photon?"],
        }

    monkeypatch.setattr("app.features.tutor.service.run_tutor_pipeline", fake_pipeline)

    headers = await _auth_header(client)
    resp = await client.post(
        "/tutor/ask", json={"question": "Why is the sky blue?"}, headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["question"] == "Why is the sky blue?"
    assert body["answer"] == "Rayleigh scattering makes the sky blue."
    assert len(body["followups"]) == 3


async def test_ask_rejects_blank_question(client, monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")
    headers = await _auth_header(client)
    resp = await client.post("/tutor/ask", json={"question": "   "}, headers=headers)
    assert resp.status_code == 422
