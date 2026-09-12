from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SubmissionCreate(BaseModel):
    requirements_assumptions: str = Field(
        ...,
        min_length=10,
        description="Your understanding of requirements, scope, and assumptions."
    )
    classes: str = Field(
        ...,
        min_length=10,
        description="Proposed classes, interfaces, and data models."
    )
    responsibilities: str = Field(
        ...,
        min_length=10,
        description="Responsibilities and methods associated with each class."
    )
    relationships: str = Field(
        ...,
        min_length=10,
        description="Relationships between classes (composition, inheritance, association)."
    )
    design_decisions: str = Field(
        ...,
        min_length=10,
        description="Architectural patterns, trade-offs, and reasoning."
    )
    edge_cases: str = Field(
        ...,
        min_length=10,
        description="Edge cases, concurrency concerns, and failure handling."
    )


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attempt_id: int
    requirements_assumptions: str
    classes: str
    responsibilities: str
    relationships: str
    design_decisions: str
    edge_cases: str
    submitted_at: datetime
