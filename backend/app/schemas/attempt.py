from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.submission import SubmissionResponse
from app.schemas.evaluation import EvaluationResponse


class AttemptCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    attempt_number: int
    status: str
    is_sample: bool = False
    created_at: datetime


class AttemptDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    problem_title: Optional[str] = None
    problem_slug: Optional[str] = None
    attempt_number: int
    status: str
    is_sample: bool = False
    created_at: datetime
    updated_at: datetime
    submission: Optional[SubmissionResponse] = None
    evaluation: Optional[EvaluationResponse] = None


class AttemptListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    problem_title: str
    problem_slug: str
    attempt_number: int
    status: str
    is_sample: bool = False
    score: Optional[int] = None
    evaluator_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
