"""API tests for the teacher dashboard feature."""


async def _login(client, email):
    resp = await client.post("/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def _teacher(client):
    return await _login(client, "teacher@school.edu")


async def test_teacher_routes_require_teacher_role(seeded_client):
    student = await _login(seeded_client, "maya.chen@school.edu")
    for path in (
        "/teacher/students",
        "/teacher/topics",
        "/teacher/escalations",
        "/teacher/overview",
    ):
        resp = await seeded_client.get(path, headers=student)
        assert resp.status_code == 403, path


async def test_roster_default_order_and_shape(seeded_client):
    h = await _teacher(seeded_client)
    body = (await seeded_client.get("/teacher/students", headers=h)).json()
    assert body["total"] == 5
    # default sort = improvement desc -> Maya first, Rohan last
    ids = [s["id"] for s in body["items"]]
    assert ids[0] == "maya" and ids[-1] == "rohan"
    maya = body["items"][0]
    assert maya["improvement"] == "+38%" and maya["tone"] == "good"
    assert maya["topics_explored"] == 4


async def test_roster_filter_and_search(seeded_client):
    h = await _teacher(seeded_client)
    at_risk = (await seeded_client.get("/teacher/students?tone=bad", headers=h)).json()
    assert [s["id"] for s in at_risk["items"]] == ["rohan"]
    found = (await seeded_client.get("/teacher/students?q=priya", headers=h)).json()
    assert [s["id"] for s in found["items"]] == ["priya"]


async def test_student_record_and_topics(seeded_client):
    h = await _teacher(seeded_client)
    rec = (await seeded_client.get("/teacher/students/maya", headers=h)).json()
    assert rec["topic_count"] == 4 and rec["total_questions"] == 8
    topics = (await seeded_client.get("/teacher/students/maya/topics", headers=h)).json()
    ids = [t["topic"]["id"] for t in topics["items"]]
    assert ids[0] == "partition"  # position order
    partition = topics["items"][0]
    assert partition["engagement"] == {"asked": 3, "u": "yes", "m": 0.7}


async def test_student_record_unknown_404(seeded_client):
    h = await _teacher(seeded_client)
    resp = await seeded_client.get("/teacher/students/nobody", headers=h)
    assert resp.status_code == 404


async def test_topics_aggregate(seeded_client):
    h = await _teacher(seeded_client)
    body = (await seeded_client.get("/teacher/topics", headers=h)).json()
    partition = next(t for t in body["items"] if t["id"] == "partition")
    # all five students engaged with partition
    assert partition["aggregate"]["students"] == 5
    assert partition["aggregate"]["understood"] == 3


async def test_topic_students_list(seeded_client):
    h = await _teacher(seeded_client)
    body = (await seeded_client.get("/teacher/topics/cmpAny/students", headers=h)).json()
    ids = {s["id"] for s in body["items"]}
    assert {"maya", "priya", "leo", "sam", "rohan"} == ids
    rohan = next(s for s in body["items"] if s["id"] == "rohan")
    assert rohan["engagement"]["u"] == "no"


async def test_escalations_and_resolve(seeded_client):
    h = await _teacher(seeded_client)
    body = (await seeded_client.get("/teacher/escalations", headers=h)).json()
    assert body["total"] == 1
    esc = body["items"][0]
    assert esc["student_name"] == "Rohan Das" and esc["trigger"] == "confusion"

    resolved = (
        await seeded_client.post(
            f"/teacher/escalations/{esc['id']}/resolve",
            json={"teacher_notes": "Reached out."},
            headers=h,
        )
    ).json()
    assert resolved["status"] == "resolved" and resolved["resolved_at"]

    open_after = (await seeded_client.get("/teacher/escalations?status=open", headers=h)).json()
    assert open_after["total"] == 0


async def test_overview_and_simulate_day(seeded_client):
    h = await _teacher(seeded_client)
    overview = (await seeded_client.get("/teacher/overview", headers=h)).json()
    assert overview["student_count"] == 5 and overview["at_risk_count"] == 1
    assert overview["teacher_name"] == "Ms. Alvarez"

    sim = (await seeded_client.post("/teacher/simulate-day", headers=h)).json()
    assert sim["advanced"] > 0
