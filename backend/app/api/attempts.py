from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.attempt_service import AttemptService
from app.schemas.attempt import AttemptDetailResponse, AttemptListItemResponse
from app.schemas.submission import SubmissionCreate
from app.schemas.evaluation import EvaluationResponse
from app.domain.exceptions import (
    AttemptNotFoundException,
    InvalidSubmissionException,
    InvalidStateTransitionException
)

router = APIRouter(prefix="/api/attempts", tags=["Attempts"])


@router.get("", response_model=List[AttemptListItemResponse])
def list_all_attempts(db: Session = Depends(get_db)):
    """Retrieve attempt history across all problems."""
    service = AttemptService(db)
    attempts = service.get_all_attempts()
    result = []
    for att in attempts:
        # Guarantee unfinished sample/demo attempts are never displayed
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


@router.get("/{attempt_id}", response_model=AttemptDetailResponse)
def get_attempt(attempt_id: int, db: Session = Depends(get_db)):
    """Retrieve complete attempt state, including submission and evaluation."""
    service = AttemptService(db)
    try:
        att = service.get_attempt(attempt_id)
        return AttemptDetailResponse(
            id=att.id,
            problem_id=att.problem_id,
            problem_title=att.problem.title if att.problem else None,
            problem_slug=att.problem.slug if att.problem else None,
            attempt_number=att.attempt_number,
            status=att.status,
            is_sample=att.is_sample,
            created_at=att.created_at,
            updated_at=att.updated_at,
            submission=att.submission,
            evaluation=att.evaluation
        )
    except AttemptNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{attempt_id}/submit", response_model=AttemptDetailResponse)
async def submit_attempt(attempt_id: int, payload: SubmissionCreate, db: Session = Depends(get_db)):
    """Submit structured LLD design for evaluation."""
    service = AttemptService(db)
    try:
        att = await service.submit_and_evaluate(attempt_id, payload)
        return AttemptDetailResponse(
            id=att.id,
            problem_id=att.problem_id,
            problem_title=att.problem.title if att.problem else None,
            problem_slug=att.problem.slug if att.problem else None,
            attempt_number=att.attempt_number,
            status=att.status,
            is_sample=att.is_sample,
            created_at=att.created_at,
            updated_at=att.updated_at,
            submission=att.submission,
            evaluation=att.evaluation
        )
    except AttemptNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidSubmissionException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors)
    except InvalidStateTransitionException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{attempt_id}/evaluation", response_model=EvaluationResponse)
def get_evaluation(attempt_id: int, db: Session = Depends(get_db)):
    """Retrieve full evaluation breakdown for a completed attempt."""
    service = AttemptService(db)
    try:
        return service.get_evaluation(attempt_id)
    except AttemptNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
