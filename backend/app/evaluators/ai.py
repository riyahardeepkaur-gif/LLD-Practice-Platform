import json
import logging
from typing import Optional
import httpx
from app.config import settings
from app.evaluators.base import BaseEvaluator
from app.evaluators.rule_based import RuleBasedEvaluator
from app.domain.models import EvaluationDomain, EvaluationCriterionDomain, EvaluatorType
from app.models.entities import ProblemModel, SubmissionModel

logger = logging.getLogger(__name__)


class AIEvaluator(BaseEvaluator):
    """
    AI-powered evaluator using an LLM (OpenAI-compatible chat completion API).
    Produces judgment-heavy feedback with grounded evidence and actionable suggestions.
    Gracefully falls back to RuleBasedEvaluator if API fails, network times out,
    or output is malformed.
    """

    def __init__(self, fallback_evaluator: Optional[BaseEvaluator] = None):
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.base_url = settings.llm_base_url.rstrip("/")
        self.fallback = fallback_evaluator or RuleBasedEvaluator(evaluator_type=EvaluatorType.AI_FALLBACK)

    async def evaluate(self, problem: ProblemModel, submission: SubmissionModel) -> EvaluationDomain:
        if not self.api_key:
            logger.info("No LLM API key configured. Executing fallback evaluator.")
            return await self.fallback.evaluate(problem, submission)

        prompt = self._build_prompt(problem, submission)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are an expert Low-Level Design (LLD) interviewer and software architect. "
                                    "Evaluate the student's LLD submission strictly against the provided requirements and rubric. "
                                    "Respond ONLY with valid JSON matching the requested schema."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.2
                    }
                )

                if response.status_code != 200:
                    logger.warning(f"LLM API returned status {response.status_code}: {response.text}. Falling back.")
                    return await self.fallback.evaluate(problem, submission)

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)

                return self._parse_evaluation(parsed, submission.attempt_id)

        except Exception as ex:
            logger.warning(f"AI evaluation failed ({str(ex)}). Using fallback evaluator.")
            return await self.fallback.evaluate(problem, submission)

    def _build_prompt(self, problem: ProblemModel, submission: SubmissionModel) -> str:
        return f"""
EVALUATION CONTEXT:
Problem Title: {problem.title}
Difficulty: {problem.difficulty}
Description: {problem.description}

Functional Requirements:
{json.dumps(problem.functional_requirements, indent=2)}

Important Considerations:
{json.dumps(problem.considerations, indent=2)}

STUDENT SUBMISSION:
1. Requirements & Assumptions:
{submission.requirements_assumptions}

2. Proposed Classes:
{submission.classes}

3. Responsibilities:
{submission.responsibilities}

4. Relationships:
{submission.relationships}

5. Design Decisions & Trade-offs:
{submission.design_decisions}

6. Edge Cases & Concurrency:
{submission.edge_cases}

EVALUATION RUBRIC:
Evaluate each of the following 7 criteria rigorously:
1. Requirement Understanding (Score 0-10)
2. Class Responsibilities (Score 0-10)
3. Encapsulation and Abstraction (Score 0-10)
4. Coupling and Cohesion (Score 0-10)
5. Extensibility (Score 0-10)
6. Edge Cases (Score 0-10)
7. Design Reasoning / Trade-offs (Score 0-10)

For each criterion provide:
- name: Criterion title
- score: Integer from 0 to 10
- evidence: Specific quotes or direct observations from the student's submission
- concern: Concrete weakness, risk, or missing element
- suggestion: Actionable guidance on how to fix or elevate the design
- confidence: Float between 0.5 and 1.0

Return a JSON object matching this exact structure:
{{
  "overall_score": <integer 0-100, weighted sum of criteria>,
  "criteria": [
    {{
      "name": "Requirement Understanding",
      "score": 8,
      "evidence": "...",
      "concern": "...",
      "suggestion": "...",
      "confidence": 0.95
    }},
    ... (all 7 criteria)
  ],
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "summary": "<Short learner-friendly executive summary of the evaluation>"
}}
"""

    def _parse_evaluation(self, data: dict, attempt_id: int) -> EvaluationDomain:
        criteria_list = []
        for item in data.get("criteria", []):
            criteria_list.append(
                EvaluationCriterionDomain(
                    name=str(item.get("name", "Evaluation Criterion")),
                    score=int(item.get("score", 5)),
                    evidence=str(item.get("evidence", "Evidence analyzed from submission.")),
                    concern=str(item.get("concern", "No major concern noted.")),
                    suggestion=str(item.get("suggestion", "Continue following standard patterns.")),
                    confidence=float(item.get("confidence", 0.9))
                )
            )

        overall = int(data.get("overall_score", 70))
        overall = max(0, min(100, overall))

        return EvaluationDomain(
            id=None,
            attempt_id=attempt_id,
            evaluator_type=EvaluatorType.AI,
            overall_score=overall,
            criteria=criteria_list,
            strengths=[str(s) for s in data.get("strengths", [])],
            improvements=[str(i) for i in data.get("improvements", [])],
            summary=str(data.get("summary", "Evaluation completed successfully."))
        )
