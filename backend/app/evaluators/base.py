from abc import ABC, abstractmethod
from app.domain.models import EvaluationDomain
from app.models.entities import ProblemModel, SubmissionModel


class BaseEvaluator(ABC):
    """Abstract interface for all LLD evaluators (Rule-based, AI, and future Human/Hybrid)."""

    @abstractmethod
    async def evaluate(self, problem: ProblemModel, submission: SubmissionModel) -> EvaluationDomain:
        """Evaluates a student's submission against the problem's requirements and rubric."""
        pass
