from typing import List
from sqlalchemy.orm import Session
from app.repositories.problem_repo import ProblemRepository
from app.models.entities import ProblemModel
from app.domain.exceptions import ProblemNotFoundException


class ProblemService:
    def __init__(self, db: Session):
        self.repo = ProblemRepository(db)

    def get_all_problems(self) -> List[ProblemModel]:
        return self.repo.get_all()

    def get_problem_by_id(self, problem_id: int) -> ProblemModel:
        problem = self.repo.get_by_id(problem_id)
        if not problem:
            raise ProblemNotFoundException(problem_id)
        return problem
