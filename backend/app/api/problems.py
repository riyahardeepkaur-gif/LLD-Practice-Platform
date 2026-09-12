from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.problem_service import ProblemService
from app.services.attempt_service import AttemptService
from app.schemas.problem import ProblemSummaryResponse, ProblemDetailResponse
from app.schemas.attempt import AttemptCreateResponse, AttemptListItemResponse
from app.domain.exceptions import ProblemNotFoundException

router = APIRouter(prefix="/api/problems", tags=["Problems"])


@router.get("", response_model=List[ProblemSummaryResponse])
def list_problems(db: Session = Depends(get_db)):
    """Retrieve all available LLD practice problems."""
    service = ProblemService(db)
    return service.get_all_problems()


@router.get("/{problem_id}", response_model=ProblemDetailResponse)
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    """Retrieve full details, requirements, and rubric for a specific problem."""
    service = ProblemService(db)
    try:
        return service.get_problem_by_id(problem_id)
    except ProblemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{problem_id}/attempts", response_model=AttemptCreateResponse, status_code=status.HTTP_201_CREATED)
def start_attempt(problem_id: int, db: Session = Depends(get_db)):
    """Start a new practice attempt for a problem."""
    service = AttemptService(db)
    try:
        return service.start_attempt(problem_id)
    except ProblemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{problem_id}/attempts", response_model=List[AttemptListItemResponse])
def list_problem_attempts(problem_id: int, db: Session = Depends(get_db)):
    """List all attempts recorded for a specific problem."""
    service = AttemptService(db)
    try:
        attempts = service.get_problem_attempts(problem_id)
        result = []
        for att in attempts:
            if att.is_sample and att.status != "COMPLETED":
                continue
            result.append(
                AttemptListItemResponse(
                    id=att.id,
                    problem_id=att.problem_id,
                    problem_title=att.problem.title if att.problem else "Unknown",
                    problem_slug=att.problem.slug if att.problem else "unknown",
                    attempt_number=att.attempt_number,
                    status=att.status,
                    is_sample=att.is_sample,
                    score=att.evaluation.overall_score if att.evaluation else None,
                    evaluator_type=att.evaluation.evaluator_type if att.evaluation else None,
                    created_at=att.created_at,
                    updated_at=att.updated_at
                )
            )
        return result
    except ProblemNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
