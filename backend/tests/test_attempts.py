def test_start_attempt_success(client):
    response = client.post("/api/problems/1/attempts")
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["problem_id"] == 1
    assert data["attempt_number"] == 1
    assert data["status"] == "STARTED"


def test_attempt_number_increments(client):
    resp1 = client.post("/api/problems/1/attempts")
    assert resp1.status_code == 201
    assert resp1.json()["attempt_number"] == 1

    resp2 = client.post("/api/problems/1/attempts")
    assert resp2.status_code == 201
    assert resp2.json()["attempt_number"] == 2


def test_start_attempt_invalid_problem(client):
    response = client.post("/api/problems/999/attempts")
    assert response.status_code == 404


def test_get_attempt_by_id(client):
    start_resp = client.post("/api/problems/1/attempts")
    attempt_id = start_resp.json()["id"]

    get_resp = client.get(f"/api/attempts/{attempt_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == attempt_id
    assert data["status"] == "STARTED"
    assert data["submission"] is None
    assert data["evaluation"] is None


def test_list_all_attempts_and_history(client):
    # Start attempts for problem 1 and problem 2
    client.post("/api/problems/1/attempts")
    client.post("/api/problems/2/attempts")

    response = client.get("/api/attempts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Problem-specific history
    prob1_resp = client.get("/api/problems/1/attempts")
    assert prob1_resp.status_code == 200
    assert len(prob1_resp.json()) == 1
    assert prob1_resp.json()[0]["problem_id"] == 1


def test_user_attempt_defaults_is_sample_false(client):
    response = client.post("/api/problems/1/attempts")
    assert response.status_code == 201
    data = response.json()
    assert data["is_sample"] is False

    get_resp = client.get(f"/api/attempts/{data['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["is_sample"] is False

    list_resp = client.get("/api/attempts")
    assert list_resp.status_code == 200
    item = next(a for a in list_resp.json() if a["id"] == data["id"])
    assert item["is_sample"] is False


def test_unfinished_sample_attempt_is_excluded_from_history(client, db_session):
    from app.models.entities import AttemptModel

    # Add an unfinished dummy attempt marked as sample
    unfinished_sample = AttemptModel(
        problem_id=1,
        attempt_number=99,
        status="STARTED",
        is_sample=True
    )
    # Add a completed attempt marked as sample
    completed_sample = AttemptModel(
        problem_id=1,
        attempt_number=1,
        status="COMPLETED",
        is_sample=True
    )
    db_session.add(unfinished_sample)
    db_session.add(completed_sample)
    db_session.commit()

    response = client.get("/api/attempts")
    assert response.status_code == 200
    attempt_ids = [a["id"] for a in response.json()]
    assert unfinished_sample.id not in attempt_ids
    assert completed_sample.id in attempt_ids
