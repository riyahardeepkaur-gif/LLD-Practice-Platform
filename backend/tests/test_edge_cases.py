import pytest
from unittest.mock import AsyncMock, patch
from app.evaluators.base import BaseEvaluator
from app.services.attempt_service import AttemptService
from app.schemas.submission import SubmissionCreate


class FailingEvaluator(BaseEvaluator):
    """An evaluator that simulates a runtime crash or external service total failure."""
    async def evaluate(self, problem, submission):
        raise RuntimeError("Simulated total evaluator crash")


@pytest.mark.asyncio
async def test_evaluation_failure_preserves_submission(db_session):
    service = AttemptService(db=db_session, evaluator=FailingEvaluator())

    # 1. Start an attempt
    attempt = service.start_attempt(problem_id=1)
    assert attempt.status == "STARTED"

    # 2. Submit payload
    payload = SubmissionCreate(
        requirements_assumptions="Comprehensive requirements for parking lot with multiple gates.",
        classes="ParkingLot, Gate, Spot, Ticket, Vehicle",
        responsibilities="Coordinates spots and tickets.",
        relationships="ParkingLot has-a Gates and Spots.",
        design_decisions="Chose strategy pattern for spot search.",
        edge_cases="Lot full, concurrent gate arrivals."
    )

    # 3. Submit and evaluate (which will fail during evaluation step)
    updated_attempt = await service.submit_and_evaluate(attempt.id, payload)

    # 4. Status should be FAILED
    assert updated_attempt.status == "FAILED"

    # 5. CRITICAL GUARANTEE: Submission content is completely preserved!
    assert updated_attempt.submission is not None
    assert updated_attempt.submission.classes == payload.classes
    assert updated_attempt.submission.requirements_assumptions == payload.requirements_assumptions
    assert updated_attempt.evaluation is None


@pytest.mark.asyncio
async def test_cannot_resubmit_to_completed_attempt(client):
    start_resp = client.post("/api/problems/1/attempts")
    attempt_id = start_resp.json()["id"]

    valid_payload = {
        "requirements_assumptions": "Comprehensive requirements for parking lot.",
        "classes": "ParkingLot, Spot, Ticket, Vehicle",
        "responsibilities": "Coordinates spots and tickets.",
        "relationships": "ParkingLot has-a Spots.",
        "design_decisions": "Chose strategy pattern for allocation.",
        "edge_cases": "Lot full, concurrent arrivals."
    }

    # First submission -> transitions to COMPLETED
    res1 = client.post(f"/api/attempts/{attempt_id}/submit", json=valid_payload)
    assert res1.status_code == 200
    assert res1.json()["status"] == "COMPLETED"

    # Second submission to completed attempt should be rejected with 400 Bad Request
    res2 = client.post(f"/api/attempts/{attempt_id}/submit", json=valid_payload)
    assert res2.status_code == 400
    assert "cannot transition" in res2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_retry_evaluation_from_failed_state(db_session):
    # Setup service with failing evaluator first
    failing_service = AttemptService(db=db_session, evaluator=FailingEvaluator())
    attempt = failing_service.start_attempt(problem_id=1)

    payload = SubmissionCreate(
        requirements_assumptions="Comprehensive requirements for parking lot.",
        classes="ParkingLot, Spot, Ticket, Vehicle",
        responsibilities="Coordinates spots and tickets.",
        relationships="ParkingLot has-a Spots.",
        design_decisions="Chose strategy pattern for allocation.",
        edge_cases="Lot full, concurrent arrivals."
    )

    failed_attempt = await failing_service.submit_and_evaluate(attempt.id, payload)
    assert failed_attempt.status == "FAILED"

    # Now simulate recovery with working default evaluator
    from app.evaluators.rule_based import RuleBasedEvaluator
    recovered_service = AttemptService(db=db_session, evaluator=RuleBasedEvaluator())

    # Retrying submission on FAILED attempt succeeds
    recovered_attempt = await recovered_service.submit_and_evaluate(attempt.id, payload)
    assert recovered_attempt.status == "COMPLETED"
    assert recovered_attempt.evaluation is not None
