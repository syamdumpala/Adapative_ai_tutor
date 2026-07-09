"""API tests for the tutor read surfaces: sessions, conversation history, profile, performance."""


async def _login(client, email="maya.chen@school.edu"):
    resp = await client.post("/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def test_sessions_list_maps_status_and_subject(seeded_client):
    h = await _login(seeded_client)
    body = (await seeded_client.get("/tutor/sessions", headers=h)).json()
    assert body["total"] == 3
    titles = {s["title"] for s in body["items"]}
    assert "Comparing 1/2 and 1/3" in titles
    statuses = {s["status"] for s in body["items"]}
    assert statuses <= {"pending", "completed"}
    f1 = next(s for s in body["items"] if s["id"] == "seed_f1")
    assert f1["subject"]["glyph"] == "½" and f1["message_count"] == 4


async def test_sessions_status_filter(seeded_client):
    h = await _login(seeded_client)
    completed = (await seeded_client.get("/tutor/sessions?status=completed", headers=h)).json()
    assert {s["id"] for s in completed["items"]} == {"seed_f1", "seed_d1"}
    pending = (await seeded_client.get("/tutor/sessions?status=pending", headers=h)).json()
    assert {s["id"] for s in pending["items"]} == {"seed_p1"}


async def test_conversation_history_sender_mapping(seeded_client):
    h = await _login(seeded_client)
    body = (await seeded_client.get("/tutor/sessions/seed_f1/messages", headers=h)).json()
    assert body["total"] == 4
    senders = [m["from"] for m in body["items"]]
    assert senders == ["maya", "tutor", "maya", "tutor"]
    assert all(m["kind"] == "text" for m in body["items"])


async def test_student_cannot_read_others_session(seeded_client):
    maya = await _login(seeded_client)
    # Rohan's escalation session belongs to another student -> 404 (no leak)
    resp = await seeded_client.get("/tutor/sessions/seed_esc_rohan/messages", headers=maya)
    assert resp.status_code == 404


async def test_teacher_can_read_any_session(seeded_client):
    teacher = await _login(seeded_client, "teacher@school.edu")
    resp = await seeded_client.get("/tutor/sessions/seed_f1", headers=teacher)
    assert resp.status_code == 200
    assert resp.json()["id"] == "seed_f1"


async def test_profile_and_performance(seeded_client):
    h = await _login(seeded_client)
    profile = (await seeded_client.get("/me/profile", headers=h)).json()
    assert profile["email"] == "maya.chen@school.edu"
    assert profile["grade"] == "Grade 5" and profile["subjects_available"] == 6
    assert profile["initials"] == "MC"

    perf = (await seeded_client.get("/me/performance", headers=h)).json()
    assert perf["recent_accuracy"] == "84%"
    assert perf["concepts_mastered"] == 12
    assert perf["misconceptions_resolving"] == 1
    assert "Whole-number bias" in perf["insight"]["text"]
    assert {s["key"] for s in perf["stats"]} == {"accuracy", "mastered", "streak", "misconception"}


async def test_topic_analytics_returns_own_concepts_in_position_order(seeded_client):
    h = await _login(seeded_client)
    body = (await seeded_client.get("/me/topics", headers=h)).json()
    topics = body["topics"]
    # Maya has engaged with four concepts; they come back ordered by concept position.
    assert [t["concept_id"] for t in topics] == ["partition", "cmpUnit", "cmpAny", "equiv"]

    part = topics[0]
    assert part["concept_name"] == "Equal partitioning"
    assert part["subject_id"] == "1" and part["subject_name"] == "Fractions"
    assert part["glyph"] == "◐" and part["tone"] == "green"
    assert part["mastery"] == 0.7 and part["confidence"] == 0.7
    assert part["understanding"] == "yes" and part["attempts"] == 3
    assert part["next_review"] is not None

    equiv = topics[-1]
    assert equiv["understanding"] == "partial" and equiv["mastery"] == 0.3


async def test_topic_analytics_scoped_to_signed_in_student(seeded_client):
    # Rohan engaged with only partition + cmpAny; he must not see Maya's other topics.
    h = await _login(seeded_client, "rohan@school.edu")
    body = (await seeded_client.get("/me/topics", headers=h)).json()
    assert {t["concept_id"] for t in body["topics"]} == {"partition", "cmpAny"}


async def test_seeded_analytics_populate_progress_charts(analytics_client):
    """The demo analytics series feeds the overall "My progress" charts with real rows."""
    from app.seed import ANALYTICS_SHAPE

    h = await _login(analytics_client)
    body = (await analytics_client.get("/me/analytics", headers=h)).json()

    points = body["points"]
    assert len(points) == ANALYTICS_SHAPE["maya"]["n"]
    # Ordered oldest→newest and trending upward (learning progress).
    assert points[-1]["mastery"] > points[0]["mastery"]
    # Some early points carry a misconception (drives the donut).
    assert any(p["misconception_category"] for p in points)
    # The signed Misconfidence Index is populated (not flat at 0) and both signs occur.
    mis = [p["misconception_index"] for p in points]
    assert any(m < 0 for m in mis) and any(m > 0 for m in mis)
    # One by-subject aggregate per distinct subject the points span.
    subjects = {p["subject_id"] for p in points}
    assert subjects >= {"1"}
    assert len(body["by_subject"]) == len(subjects)
