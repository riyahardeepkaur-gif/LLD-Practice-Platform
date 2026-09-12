def test_get_all_problems(client):
    response = client.get("/api/problems")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    slugs = [p["slug"] for p in data]
    assert "parking-lot" in slugs
    assert "elevator-system" in slugs
    assert "vending-machine" in slugs


def test_get_problem_by_id_success(client):
    # Fetch first problem (Parking Lot)
    response = client.get("/api/problems/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["slug"] == "parking-lot"
    assert data["title"] == "Parking Lot"
    assert "functional_requirements" in data
    assert len(data["functional_requirements"]) > 0
    assert "considerations" in data
    assert "evaluation_rubric" in data
    assert len(data["evaluation_rubric"]) == 7


def test_get_problem_not_found(client):
    response = client.get("/api/problems/9999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
