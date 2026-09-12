from app.config import settings
from app.evaluators.base import BaseEvaluator
from app.evaluators.rule_based import RuleBasedEvaluator
from app.evaluators.ai import AIEvaluator
from app.domain.models import EvaluatorType


def get_evaluator() -> BaseEvaluator:
    """
    Factory function returning the configured Evaluator strategy.
    - If LLM_API_KEY is configured, returns AIEvaluator with fallback to RuleBased.
    - Otherwise returns deterministic RuleBasedEvaluator.
    """
    if settings.has_llm_configured:
        return AIEvaluator(fallback_evaluator=RuleBasedEvaluator(evaluator_type=EvaluatorType.AI_FALLBACK))
    return RuleBasedEvaluator(evaluator_type=EvaluatorType.RULE_BASED)
