"""API tests for the catalog feature (subjects + topics)."""


async def _login(client, email="maya.chen@school.edu"):
    resp = await client.post("/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def test_subjects_list_requires_auth(seeded_client):
    resp = await seeded_client.get("/subjects")
    assert resp.status_code == 401


async def test_subjects_list_envelope_and_progress(seeded_client):
    h = await _login(seeded_client)
    body = (await seeded_client.get("/subjects", headers=h)).json()
    assert body["total"] == 6
    assert {"items", "total", "limit", "offset", "has_more"} <= body.keys()
    fractions = next(s for s in body["items"] if s["id"] == "fractions")
    assert fractions["progress"] > 0  # Maya has per-concept mastery in fractions
    decimals = next(s for s in body["items"] if s["id"] == "decimals")
    assert decimals["is_new"] is True and decimals["progress"] == 0.0


async def test_subjects_search_filter_sort_paginate(seeded_client):
    h = await _login(seeded_client)
    search = (await seeded_client.get("/subjects?q=decimal", headers=h)).json()
    assert [s["id"] for s in search["items"]] == ["decimals"]

    new_only = (await seeded_client.get("/subjects?is_new=true", headers=h)).json()
    assert all(s["is_new"] for s in new_only["items"])

    page = (await seeded_client.get("/subjects?limit=2&sort=name", headers=h)).json()
    assert len(page["items"]) == 2 and page["has_more"] is True
    names = [s["name"] for s in page["items"]]
    assert names == sorted(names)


async def test_subjects_invalid_sort_is_422(seeded_client):
    h = await _login(seeded_client)
    resp = await seeded_client.get("/subjects?sort=bogus", headers=h)
    assert resp.status_code == 422


async def test_topics_list_and_filter(seeded_client):
    h = await _login(seeded_client)
    body = (await seeded_client.get("/topics?subject_id=fractions", headers=h)).json()
    assert body["total"] == 6
    assert body["items"][0]["id"] == "partition"  # default position order

    search = (await seeded_client.get("/topics?q=partition", headers=h)).json()
    assert any(t["id"] == "partition" for t in search["items"])


async def test_topic_create_requires_teacher(seeded_client):
    student = await _login(seeded_client)
    payload = {"id": "newtopic", "subject_id": "fractions", "name": "New Topic"}
    denied = await seeded_client.post("/topics", json=payload, headers=student)
    assert denied.status_code == 403

    teacher = await _login(seeded_client, "teacher@school.edu")
    created = await seeded_client.post("/topics", json=payload, headers=teacher)
    assert created.status_code == 201
    assert created.json()["id"] == "newtopic"


async def test_subject_detail_includes_concepts(seeded_client):
    h = await _login(seeded_client)
    body = (await seeded_client.get("/subjects/fractions", headers=h)).json()
    assert body["id"] == "fractions"
    assert len(body["concepts"]) == 6


async def test_subject_update_by_teacher(seeded_client):
    teacher = await _login(seeded_client, "teacher@school.edu")
    resp = await seeded_client.patch(
        "/subjects/fractions", json={"desc": "Updated blurb"}, headers=teacher
    )
    assert resp.status_code == 200 and resp.json()["desc"] == "Updated blurb"
