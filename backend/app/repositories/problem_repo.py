from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.entities import ProblemModel


class ProblemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[ProblemModel]:
        return self.db.query(ProblemModel).order_by(ProblemModel.id.asc()).all()

    def get_by_id(self, problem_id: int) -> Optional[ProblemModel]:
        return self.db.query(ProblemModel).filter(ProblemModel.id == problem_id).first()

    def get_by_slug(self, slug: str) -> Optional[ProblemModel]:
        return self.db.query(ProblemModel).filter(ProblemModel.slug == slug).first()
