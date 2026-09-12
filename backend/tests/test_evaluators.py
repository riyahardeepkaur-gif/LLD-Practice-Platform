import pytest
from app.evaluators.rule_based import RuleBasedEvaluator
from app.evaluators.ai import AIEvaluator
from app.domain.models import EvaluatorType
from app.models.entities import ProblemModel, SubmissionModel


@pytest.mark.asyncio
async def test_rule_based_evaluator_rubric_structure():
    evaluator = RuleBasedEvaluator()
    problem = ProblemModel(
        id=1,
        slug="parking-lot",
        title="Parking Lot",
        difficulty="Medium",
        description="Design a parking lot",
        functional_requirements=["req1"],
        considerations=["cons1"],
        evaluation_rubric=[{"name": "Rubric"}]
    )
    submission = SubmissionModel(
        id=1,
        attempt_id=1,
        requirements_assumptions="Design a multi-floor parking lot with spots for vehicles, tickets, and fee rates.",
        classes="ParkingLot, ParkingFloor, ParkingSpot, Vehicle, Ticket, Payment, Strategy",
        responsibilities="ParkingLot manages floors, ParkingFloor manages spots, Ticket tracks time.",
        relationships="ParkingLot has-a list of ParkingFloor. ParkingFloor has-a list of ParkingSpot. Composition.",
        design_decisions="Used Strategy pattern for spot allocation. Trade-off: simplicity vs concurrent throughput.",
        edge_cases="Handled full capacity, concurrency race conditions, and lost tickets."
    )

    result = await evaluator.evaluate(problem, submission)

    assert result.evaluator_type == EvaluatorType.RULE_BASED
    assert 0 <= result.overall_score <= 100
    assert len(result.criteria) == 7

    criterion_names = [c.name for c in result.criteria]
    assert "Requirement Understanding" in criterion_names
    assert "Class Responsibilities" in criterion_names
    assert "Encapsulation and Abstraction" in criterion_names
    assert "Coupling and Cohesion" in criterion_names
    assert "Extensibility" in criterion_names
    assert "Edge Cases" in criterion_names
    assert "Design Reasoning / Trade-offs" in criterion_names

    for c in result.criteria:
        assert 0 <= c.score <= 10
        assert len(c.evidence) > 0
        assert len(c.concern) > 0
        assert len(c.suggestion) > 0
        assert 0.0 <= c.confidence <= 1.0


@pytest.mark.asyncio
async def test_ai_evaluator_graceful_fallback():
    # AIEvaluator without API key falls back to RuleBasedEvaluator with AI_FALLBACK type
    evaluator = AIEvaluator()
    evaluator.api_key = None  # Ensure no key

    problem = ProblemModel(
        id=2,
        slug="elevator-system",
        title="Elevator System",
        difficulty="Medium",
        description="Design elevator system",
        functional_requirements=["req"],
        considerations=["cons"],
        evaluation_rubric=[]
    )
    submission = SubmissionModel(
        id=2,
        attempt_id=2,
        requirements_assumptions="Elevator system with multiple cars and floors.",
        classes="ElevatorController, ElevatorCar, Request, Door",
        responsibilities="ElevatorController dispatches, ElevatorCar moves.",
        relationships="ElevatorController has-a ElevatorCar.",
        design_decisions="Used LOOK algorithm for dispatching.",
        edge_cases="Handled overload, power failure, emergency stop."
    )

    result = await evaluator.evaluate(problem, submission)

    # Conceptually distinct evaluator type: AI_FALLBACK
    assert result.evaluator_type == EvaluatorType.AI_FALLBACK
    assert result.overall_score > 0
    assert len(result.criteria) == 7
