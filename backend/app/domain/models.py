from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any


def utcnow():
    return datetime.now(timezone.utc)


class AttemptStatus(str, Enum):
    STARTED = "STARTED"
    SUBMITTED = "SUBMITTED"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EvaluatorType(str, Enum):
    RULE_BASED = "RULE_BASED"
    AI = "AI"
    AI_FALLBACK = "AI_FALLBACK"


@dataclass
class EvaluationCriterionDomain:
    name: str
    score: int
    evidence: str
    concern: str
    suggestion: str
    confidence: float


@dataclass
class EvaluationDomain:
    id: Optional[int]
    attempt_id: int
    evaluator_type: EvaluatorType
    overall_score: int
    criteria: List[EvaluationCriterionDomain]
    strengths: List[str]
    improvements: List[str]
    summary: str
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class SubmissionDomain:
    id: Optional[int]
    attempt_id: int
    requirements_assumptions: str
    classes: str
    responsibilities: str
    relationships: str
    design_decisions: str
    edge_cases: str
    submitted_at: datetime = field(default_factory=utcnow)

    def validate_content(self) -> List[str]:
        """Validates that mandatory fields have meaningful content."""
        errors: List[str] = []
        fields = {
            "Requirements & Assumptions": self.requirements_assumptions,
            "Classes": self.classes,
            "Responsibilities": self.responsibilities,
            "Relationships": self.relationships,
            "Design Decisions & Trade-offs": self.design_decisions,
            "Edge Cases": self.edge_cases,
        }
        for name, value in fields.items():
            if not value or not value.strip():
                errors.append(f"'{name}' cannot be empty.")
            elif len(value.strip()) < 10:
                errors.append(f"'{name}' must contain at least 10 characters of explanation.")
        return errors


@dataclass
class AttemptDomain:
    id: Optional[int]
    problem_id: int
    attempt_number: int
    status: AttemptStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    submission: Optional[SubmissionDomain] = None
    evaluation: Optional[EvaluationDomain] = None

    def can_transition_to(self, new_status: AttemptStatus) -> bool:
        valid_transitions = {
            AttemptStatus.STARTED: [AttemptStatus.SUBMITTED],
            AttemptStatus.SUBMITTED: [AttemptStatus.EVALUATING],
            AttemptStatus.EVALUATING: [AttemptStatus.COMPLETED, AttemptStatus.FAILED],
            AttemptStatus.FAILED: [AttemptStatus.EVALUATING],  # Allows retrying evaluation
            AttemptStatus.COMPLETED: [],  # Terminal state
        }
        return new_status in valid_transitions.get(self.status, [])

    def transition_to(self, new_status: AttemptStatus) -> None:
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition attempt from {self.status.value} to {new_status.value}")
        self.status = new_status
        self.updated_at = datetime.utcnow()


@dataclass
class ProblemDomain:
    id: Optional[int]
    slug: str
    title: str
    difficulty: str
    description: str
    functional_requirements: List[str]
    considerations: List[str]
    evaluation_rubric: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.utcnow)
