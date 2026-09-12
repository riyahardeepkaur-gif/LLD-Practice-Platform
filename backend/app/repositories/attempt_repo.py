from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.models.entities import AttemptModel, SubmissionModel, EvaluationModel, EvaluationCriterionModel
from app.domain.models import EvaluationDomain, SubmissionDomain


def utcnow():
    return datetime.now(timezone.utc)


class AttemptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_next_attempt_number(self, problem_id: int) -> int:
        count = (
            self.db.query(AttemptModel)
            .filter(AttemptModel.problem_id == problem_id, AttemptModel.is_sample.is_(False))
            .count()
        )
        return count + 1

    def create(self, problem_id: int, is_sample: bool = False) -> AttemptModel:
        attempt_number = self.get_next_attempt_number(problem_id)
        attempt = AttemptModel(
            problem_id=problem_id,
            attempt_number=attempt_number,
            status="STARTED",
            is_sample=is_sample,
            created_at=utcnow(),
            updated_at=utcnow()
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_by_id(self, attempt_id: int) -> Optional[AttemptModel]:
        return (
            self.db.query(AttemptModel)
            .options(
                joinedload(AttemptModel.problem),
                joinedload(AttemptModel.submission),
                joinedload(AttemptModel.evaluation).joinedload(EvaluationModel.criteria)
            )
            .filter(AttemptModel.id == attempt_id)
            .first()
        )

    def get_all(self, include_unfinished_sample: bool = False) -> List[AttemptModel]:
        query = (
            self.db.query(AttemptModel)
            .options(
                joinedload(AttemptModel.problem),
                joinedload(AttemptModel.evaluation)
            )
        )
        if not include_unfinished_sample:
            query = query.filter(or_(AttemptModel.is_sample.is_(False), AttemptModel.status == "COMPLETED"))
        return query.order_by(AttemptModel.created_at.desc()).all()

    def get_by_problem_id(self, problem_id: int, include_unfinished_sample: bool = False) -> List[AttemptModel]:
        query = (
            self.db.query(AttemptModel)
            .options(
                joinedload(AttemptModel.problem),
                joinedload(AttemptModel.evaluation)
            )
            .filter(AttemptModel.problem_id == problem_id)
        )
        if not include_unfinished_sample:
            query = query.filter(or_(AttemptModel.is_sample.is_(False), AttemptModel.status == "COMPLETED"))
        return query.order_by(AttemptModel.attempt_number.desc()).all()

    def update_status(self, attempt_id: int, status: str) -> Optional[AttemptModel]:
        attempt = self.db.query(AttemptModel).filter(AttemptModel.id == attempt_id).first()
        if attempt:
            attempt.status = status
            attempt.updated_at = utcnow()
            self.db.commit()
            self.db.refresh(attempt)
        return attempt

    def save_submission(self, attempt_id: int, data: dict) -> SubmissionModel:
        submission = self.db.query(SubmissionModel).filter(SubmissionModel.attempt_id == attempt_id).first()
        if submission:
            for k, v in data.items():
                setattr(submission, k, v)
            submission.submitted_at = utcnow()
        else:
            submission = SubmissionModel(
                attempt_id=attempt_id,
                **data,
                submitted_at=utcnow()
            )
            self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def save_evaluation(self, attempt_id: int, evaluation_domain: EvaluationDomain) -> EvaluationModel:
        evaluation = self.db.query(EvaluationModel).filter(EvaluationModel.attempt_id == attempt_id).first()
        if evaluation:
            self.db.delete(evaluation)
            self.db.flush()

        evaluation = EvaluationModel(
            attempt_id=attempt_id,
            evaluator_type=evaluation_domain.evaluator_type.value,
            overall_score=evaluation_domain.overall_score,
            strengths=evaluation_domain.strengths,
            improvements=evaluation_domain.improvements,
            summary=evaluation_domain.summary,
            created_at=utcnow()
        )
        self.db.add(evaluation)
        self.db.flush()

        for c in evaluation_domain.criteria:
            crit = EvaluationCriterionModel(
                evaluation_id=evaluation.id,
                name=c.name,
                score=c.score,
                evidence=c.evidence,
                concern=c.concern,
                suggestion=c.suggestion,
                confidence=c.confidence
            )
            self.db.add(crit)

        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation
