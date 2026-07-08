"""Unit / API tests for the auth feature."""

REGISTRATION = {
    "student_name": "Ada Lovelace",
    "student_id": "S001",
    "email": "ada@example.com",
    "password": "secret123",
}


async def _register(client, **overrides):
    payload = {**REGISTRATION, **overrides}
    return await client.post("/auth/register", json=payload)


async def test_register_success(client):
    resp = await _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "ada@example.com"
    assert body["student_id"] == "S001"
    assert "id" in body
    # Never leak the password hash.
    assert "hashed_password" not in body
    assert "password" not in body


async def test_register_duplicate_email(client):
    await _register(client)
    resp = await _register(client, student_id="S002")  # same email
    assert resp.status_code == 409


async def test_register_rejects_weak_password(client):
    too_short = await _register(client, password="ab1")
    assert too_short.status_code == 422

    no_digit = await _register(
        client, email="b@example.com", student_id="S9", password="alphabetonly"
    )
    assert no_digit.status_code == 422


async def test_register_rejects_bad_student_id(client):
    resp = await _register(client, student_id="has spaces!")
    assert resp.status_code == 422


async def test_login_and_me(client):
    await _register(client)
    login = await client.post(
        "/auth/login",
        json={"email": REGISTRATION["email"], "password": REGISTRATION["password"]},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["student_id"] == "S001"


async def test_oauth2_token_form(client):
    """The Swagger 'Authorize' dialog posts form-encoded username/password here."""
    await _register(client)
    resp = await client.post(
        "/auth/token",
        data={"username": REGISTRATION["email"], "password": REGISTRATION["password"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"

    # The issued token works against a protected route.
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200


async def test_login_wrong_password(client):
    await _register(client)
    resp = await client.post(
        "/auth/login",
        json={"email": REGISTRATION["email"], "password": "wrongpass1"},
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401
