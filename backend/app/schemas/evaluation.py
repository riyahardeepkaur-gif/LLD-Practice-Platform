from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class EvaluationCriterionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    score: int = Field(..., ge=0, le=10)
    evidence: str
    concern: str
    suggestion: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attempt_id: int
    evaluator_type: str
    overall_score: int
    criteria: List[EvaluationCriterionSchema]
    strengths: List[str]
    improvements: List[str]
    summary: str
    created_at: datetime
