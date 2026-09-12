class DomainException(Exception):
    """Base domain exception."""
    pass


class ProblemNotFoundException(DomainException):
    def __init__(self, problem_id: int):
        super().__init__(f"Problem with ID {problem_id} was not found.")
        self.problem_id = problem_id


class AttemptNotFoundException(DomainException):
    def __init__(self, attempt_id: int):
        super().__init__(f"Attempt with ID {attempt_id} was not found.")
        self.attempt_id = attempt_id


class InvalidSubmissionException(DomainException):
    def __init__(self, errors: list[str]):
        super().__init__(f"Invalid submission: {'; '.join(errors)}")
        self.errors = errors


class InvalidStateTransitionException(DomainException):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(f"Cannot transition attempt from {current_status} to {target_status}.")
        self.current_status = current_status
        self.target_status = target_status


class EvaluationFailedException(DomainException):
    def __init__(self, reason: str):
        super().__init__(f"Evaluation failed: {reason}")
        self.reason = reason
