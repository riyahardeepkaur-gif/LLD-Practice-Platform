from typing import List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ProblemSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    difficulty: str
    description: str


class ProblemDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    difficulty: str
    description: str
    functional_requirements: List[str]
    considerations: List[str]
    evaluation_rubric: List[Dict[str, Any]]
