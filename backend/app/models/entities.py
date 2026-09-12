from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class ProblemModel(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    difficulty = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    functional_requirements = Column(JSON, nullable=False)
    considerations = Column(JSON, nullable=False)
    evaluation_rubric = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    attempts = relationship("AttemptModel", back_populates="problem", cascade="all, delete-orphan")


class AttemptModel(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(50), default="STARTED", nullable=False)
    is_sample = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    problem = relationship("ProblemModel", back_populates="attempts")
    submission = relationship("SubmissionModel", back_populates="attempt", uselist=False, cascade="all, delete-orphan")
    evaluation = relationship("EvaluationModel", back_populates="attempt", uselist=False, cascade="all, delete-orphan")


class SubmissionModel(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), unique=True, nullable=False)
    requirements_assumptions = Column(Text, nullable=False)
    classes = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=False)
    relationships = Column(Text, nullable=False)
    design_decisions = Column(Text, nullable=False)
    edge_cases = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=utcnow)

    attempt = relationship("AttemptModel", back_populates="submission")


class EvaluationModel(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), unique=True, nullable=False)
    evaluator_type = Column(String(50), nullable=False)
    overall_score = Column(Integer, nullable=False)
    strengths = Column(JSON, nullable=False)
    improvements = Column(JSON, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    attempt = relationship("AttemptModel", back_populates="evaluation")
    criteria = relationship("EvaluationCriterionModel", back_populates="evaluation", cascade="all, delete-orphan")


class EvaluationCriterionModel(Base):
    __tablename__ = "evaluation_criteria"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    evidence = Column(Text, nullable=False)
    concern = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)

    evaluation = relationship("EvaluationModel", back_populates="criteria")
