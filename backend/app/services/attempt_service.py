import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.attempt_repo import AttemptRepository
from app.repositories.problem_repo import ProblemRepository
from app.models.entities import AttemptModel, EvaluationModel
from app.schemas.submission import SubmissionCreate
from app.evaluators.factory import get_evaluator
from app.evaluators.base import BaseEvaluator
from app.domain.exceptions import (
    AttemptNotFoundException,
    ProblemNotFoundException,
    InvalidSubmissionException,
    InvalidStateTransitionException
)

logger = logging.getLogger(__name__)


class AttemptService:
    def __init__(self, db: Session, evaluator: Optional[BaseEvaluator] = None):
        self.db = db
        self.attempt_repo = AttemptRepository(db)
        self.problem_repo = ProblemRepository(db)
        self.evaluator = evaluator or get_evaluator()

    def start_attempt(self, problem_id: int) -> AttemptModel:
        problem = self.problem_repo.get_by_id(problem_id)
        if not problem:
            raise ProblemNotFoundException(problem_id)
        return self.attempt_repo.create(problem_id)

    def get_attempt(self, attempt_id: int) -> AttemptModel:
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise AttemptNotFoundException(attempt_id)
        return attempt

    def get_all_attempts(self) -> List[AttemptModel]:
        return self.attempt_repo.get_all()

    def get_problem_attempts(self, problem_id: int) -> List[AttemptModel]:
        problem = self.problem_repo.get_by_id(problem_id)
        if not problem:
            raise ProblemNotFoundException(problem_id)
        return self.attempt_repo.get_by_problem_id(problem_id)

    def get_evaluation(self, attempt_id: int) -> EvaluationModel:
        attempt = self.get_attempt(attempt_id)
        if not attempt.evaluation:
            raise AttemptNotFoundException(attempt_id)
        return attempt.evaluation

    async def submit_and_evaluate(self, attempt_id: int, submission_data: SubmissionCreate) -> AttemptModel:
        attempt = self.get_attempt(attempt_id)

        # Allow submission only from STARTED or FAILED (retry evaluation)
        if attempt.status not in ["STARTED", "FAILED"]:
            raise InvalidStateTransitionException(
                current_status=attempt.status,
                target_status="SUBMITTED"
            )

        # 1. Deterministic validation of input
        errors = []
        fields = {
            "requirements_assumptions": submission_data.requirements_assumptions,
            "classes": submission_data.classes,
            "responsibilities": submission_data.responsibilities,
            "relationships": submission_data.relationships,
            "design_decisions": submission_data.design_decisions,
            "edge_cases": submission_data.edge_cases,
        }
        for name, value in fields.items():
            if not value or not value.strip():
                errors.append(f"Field '{name}' cannot be empty.")
            elif len(value.strip()) < 10:
                errors.append(f"Field '{name}' must contain at least 10 characters.")

        if errors:
            raise InvalidSubmissionException(errors)

        # 2. Persist submission and set state to SUBMITTED
        submission = self.attempt_repo.save_submission(attempt_id, fields)
        self.attempt_repo.update_status(attempt_id, "SUBMITTED")

        # 3. Transition state to EVALUATING
        self.attempt_repo.update_status(attempt_id, "EVALUATING")

        # 4. Perform evaluation
        try:
            problem = self.problem_repo.get_by_id(attempt.problem_id)
            evaluation_result = await self.evaluator.evaluate(problem, submission)

            # Persist evaluation and transition to COMPLETED
            self.attempt_repo.save_evaluation(attempt_id, evaluation_result)
            self.attempt_repo.update_status(attempt_id, "COMPLETED")
        except Exception as ex:
            # Preservation guarantee: Submission remains safe in database!
            logger.error(f"Evaluation failed for attempt {attempt_id}: {str(ex)}", exc_info=True)
            self.attempt_repo.update_status(attempt_id, "FAILED")

        # Reload full attempt with relations
        return self.get_attempt(attempt_id)
