import pytest

VALID_PARKING_LOT_SUBMISSION = {
    "requirements_assumptions": (
        "Designing a multi-floor parking lot system supporting motorcycles, compact cars, and large buses. "
        "Each floor has a fixed number of slots. Assumes vehicles get tickets at entry and pay hourly rates upon exit."
    ),
    "classes": (
        "ParkingLot: Singleton manager holding floors and gates.\n"
        "ParkingFloor: Contains collection of ParkingSpot instances and floor display board.\n"
        "ParkingSpot (Abstract): Subclassed by CompactSpot, LargeSpot, MotorcycleSpot.\n"
        "Vehicle (Abstract): Subclassed by Motorcycle, Car, Bus.\n"
        "Ticket: Stores id, assigned spot, entry timestamp, vehicle info.\n"
        "Payment: Handles fee calculation and processing.\n"
        "ParkingStrategy (Interface): Determines nearest available spot."
    ),
    "responsibilities": (
        "ParkingLot: Coordinates entry/exit gates and overall spot allocations.\n"
        "ParkingFloor: Tracks spot statuses (available/occupied) for that floor.\n"
        "ParkingSpot: Holds vehicle and checks compatibility.\n"
        "Ticket: Immutable record for parked duration and spot assignment.\n"
        "Payment: Calculates fee based on hourly rate table and duration."
    ),
    "relationships": (
        "ParkingLot has-a (composition) list of ParkingFloor.\n"
        "ParkingFloor has-a (composition) list of ParkingSpot.\n"
        "Vehicle is-a polymorphic hierarchy.\n"
        "Ticket associates ParkingSpot with Vehicle.\n"
        "ParkingLot uses-a ParkingStrategy to find optimal spot."
    ),
    "design_decisions": (
        "Used Strategy Pattern for parking slot allocation so algorithms (nearest to entry vs lowest floor) are swappable. "
        "Separated fee calculation into PaymentStrategy for extensible pricing rules. "
        "Trade-off: Chose thread-safe synchronizations on spots over floor-level locks to maximize entry throughput."
    ),
    "edge_cases": (
        "1. Full capacity: All spots filled returns graceful LotFullException without issuing ticket.\n"
        "2. Concurrent entry: Two vehicles entering simultaneously at separate gates allocated distinct spots via atomic locks.\n"
        "3. Lost ticket: Support manual plate lookup with flat maximum lost-ticket penalty fee."
    )
}


def test_reject_empty_or_short_submission(client):
    start_resp = client.post("/api/problems/1/attempts")
    attempt_id = start_resp.json()["id"]

    # Incomplete submission payload
    invalid_payload = {
        "requirements_assumptions": "Too short",
        "classes": "",
        "responsibilities": "Short",
        "relationships": "   ",
        "design_decisions": "",
        "edge_cases": ""
    }

    resp = client.post(f"/api/attempts/{attempt_id}/submit", json=invalid_payload)
    assert resp.status_code == 422
    data = resp.json()
    assert "detail" in data


def test_valid_submission_persistence_and_evaluation(client):
    start_resp = client.post("/api/problems/1/attempts")
    attempt_id = start_resp.json()["id"]

    # Submit valid design
    submit_resp = client.post(f"/api/attempts/{attempt_id}/submit", json=VALID_PARKING_LOT_SUBMISSION)
    assert submit_resp.status_code == 200
    attempt_data = submit_resp.json()

    # Verify status transitioned to COMPLETED
    assert attempt_data["status"] == "COMPLETED"
    assert attempt_data["submission"] is not None
    assert attempt_data["submission"]["classes"] == VALID_PARKING_LOT_SUBMISSION["classes"]

    # Verify evaluation was created
    assert attempt_data["evaluation"] is not None
    eval_data = attempt_data["evaluation"]
    assert eval_data["overall_score"] > 0
    assert len(eval_data["criteria"]) == 7
    assert len(eval_data["strengths"]) > 0
    assert len(eval_data["improvements"]) > 0

    # Test GET /api/attempts/{id}/evaluation endpoint
    eval_resp = client.get(f"/api/attempts/{attempt_id}/evaluation")
    assert eval_resp.status_code == 200
    assert eval_resp.json()["id"] == eval_data["id"]
    assert eval_resp.json()["overall_score"] == eval_data["overall_score"]
