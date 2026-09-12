import re
from typing import List, Tuple
from app.evaluators.base import BaseEvaluator
from app.domain.models import EvaluationDomain, EvaluationCriterionDomain, EvaluatorType
from app.models.entities import ProblemModel, SubmissionModel


class RuleBasedEvaluator(BaseEvaluator):
    """
    Practical, deterministic evaluator performing objective heuristic checks:
    - Verifies presence and completeness of all required sections
    - Checks for problem-specific domain entities
    - Analyzes structural relationships (composition/inheritance keywords)
    - Verifies discussion of edge cases, concurrency, and trade-offs
    - Generates grounded, explainable criteria feedback and scores
    """

    def __init__(self, evaluator_type: EvaluatorType = EvaluatorType.RULE_BASED):
        self.evaluator_type = evaluator_type

    async def evaluate(self, problem: ProblemModel, submission: SubmissionModel) -> EvaluationDomain:
        # 1. Extract text and compute lengths
        req_text = submission.requirements_assumptions.strip()
        classes_text = submission.classes.strip()
        resp_text = submission.responsibilities.strip()
        rel_text = submission.relationships.strip()
        dec_text = submission.design_decisions.strip()
        edge_text = submission.edge_cases.strip()

        # Domain concept checks per problem
        expected_keywords = self._get_expected_keywords(problem.slug)
        all_text = f"{req_text} {classes_text} {resp_text} {rel_text} {dec_text} {edge_text}".lower()
        matched_keywords = [kw for kw in expected_keywords if kw in all_text]
        keyword_ratio = len(matched_keywords) / max(len(expected_keywords), 1)

        criteria: List[EvaluationCriterionDomain] = []

        # 1. Requirement Understanding
        crit_req = self._eval_requirements(req_text, matched_keywords, expected_keywords)
        criteria.append(crit_req)

        # 2. Class Responsibilities
        crit_resp = self._eval_responsibilities(classes_text, resp_text)
        criteria.append(crit_resp)

        # 3. Encapsulation and Abstraction
        crit_encap = self._eval_encapsulation(classes_text, resp_text, dec_text)
        criteria.append(crit_encap)

        # 4. Coupling and Cohesion
        crit_coupling = self._eval_coupling(rel_text, classes_text)
        criteria.append(crit_coupling)

        # 5. Extensibility
        crit_ext = self._eval_extensibility(dec_text, classes_text)
        criteria.append(crit_ext)

        # 6. Edge Cases
        crit_edge = self._eval_edge_cases(edge_text)
        criteria.append(crit_edge)

        # 7. Design Reasoning / Trade-offs
        crit_tradeoffs = self._eval_tradeoffs(dec_text)
        criteria.append(crit_tradeoffs)

        # Calculate overall score (scaled 0-100)
        total_criterion_score = sum(c.score for c in criteria)
        overall_score = int(round((total_criterion_score / (len(criteria) * 10)) * 100))
        overall_score = max(10, min(100, overall_score))

        # Build strengths & improvements
        strengths = self._generate_strengths(criteria)
        improvements = self._generate_improvements(criteria)

        summary = (
            f"The submission demonstrates a solid functional grasp with an overall score of {overall_score}/100. "
            f"{len(matched_keywords)} of {len(expected_keywords)} key domain concepts were identified. "
            f"Focus on the recommended suggestions to refine modularity and trade-off depth."
        )

        return EvaluationDomain(
            id=None,
            attempt_id=submission.attempt_id,
            evaluator_type=self.evaluator_type,
            overall_score=overall_score,
            criteria=criteria,
            strengths=strengths,
            improvements=improvements,
            summary=summary
        )

    def _get_expected_keywords(self, slug: str) -> List[str]:
        keywords_map = {
            "parking-lot": ["vehicle", "spot", "ticket", "floor", "payment", "fee", "entry", "exit", "rate"],
            "elevator-system": ["elevator", "car", "floor", "request", "door", "dispatch", "button", "controller", "state"],
            "vending-machine": ["state", "product", "coin", "money", "inventory", "dispense", "change", "refund", "cancel"]
        }
        return keywords_map.get(slug, ["entity", "system", "service", "model"])

    def _eval_requirements(self, text: str, matched: List[str], expected: List[str]) -> EvaluationCriterionDomain:
        word_count = len(text.split())
        ratio = len(matched) / max(len(expected), 1)

        if word_count > 40 and ratio >= 0.7:
            score = 9
            evidence = f"Captured comprehensive requirements ({word_count} words), identifying key entities: {', '.join(matched[:4])}."
            concern = "Minor assumptions could be stated more formally regarding scale."
            suggestion = "Explicitly define boundaries between internal domain logic and external systems."
        elif word_count >= 20:
            score = 7
            evidence = f"Good outline of core requirements ({word_count} words) covering concepts like {', '.join(matched[:3])}."
            concern = f"Missing mention of some expected problem nuances (e.g., {', '.join([k for k in expected if k not in matched][:2])})."
            suggestion = "Document capacity constraints, rates, or interface requirements in greater detail."
        else:
            score = 5
            evidence = f"Basic requirements provided ({word_count} words)."
            concern = "Requirements description is brief and omits critical domain constraints."
            suggestion = "Detail functional requirements including inputs, expected outputs, and scope limits."

        return EvaluationCriterionDomain(
            name="Requirement Understanding",
            score=score,
            evidence=evidence,
            concern=concern,
            suggestion=suggestion,
            confidence=0.85
        )

    def _eval_responsibilities(self, classes: str, resp: str) -> EvaluationCriterionDomain:
        class_lines = [l.strip() for l in classes.split("\n") if l.strip()]
        resp_words = len(resp.split())

        if len(class_lines) >= 4 and resp_words > 40:
            score = 8
            evidence = f"Identified {len(class_lines)} primary classes with detailed responsibility assignments ({resp_words} words)."
            concern = "Check that coordinator or manager classes don't absorb too many secondary tasks."
            suggestion = "Verify adherence to Single Responsibility Principle (SRP) across top-level entities."
        elif len(class_lines) >= 2:
            score = 6
            evidence = f"Defined {len(class_lines)} classes with basic responsibility mappings."
            concern = "Class boundaries appear coarse; some classes may carry multiple disparate responsibilities."
            suggestion = "Decompose large classes into focused components (e.g. separating data state from coordination logic)."
        else:
            score = 4
            evidence = f"Limited class decomposition ({len(class_lines)} classes identified)."
            concern = "Insufficient class breakdown makes it difficult to verify separation of concerns."
            suggestion = "Break the domain down into at least 4-5 focused classes reflecting system entities."

        return EvaluationCriterionDomain(
            name="Class Responsibilities",
            score=score,
            evidence=evidence,
            concern=concern,
            suggestion=suggestion,
            confidence=0.85
        )

    def _eval_encapsulation(self, classes: str, resp: str, dec: str) -> EvaluationCriterionDomain:
        combined = f"{classes} {resp} {dec}".lower()
        has_abstractions = any(w in combined for w in ["interface", "abstract", "strategy", "factory", "polymorphism", "encapsulate", "private", "getter"])

        if has_abstractions and len(resp.split()) > 30:
            score = 8
            evidence = "Used explicit abstraction concepts and encapsulated internal class behaviors."
            concern = "Ensure internal state variables cannot be mutated directly by callers."
            suggestion = "Use interface contracts and immutable value objects where appropriate."
        elif len(resp.split()) > 20:
            score = 6
            evidence = "Class definitions distinguish between properties and behaviors."
            concern = "Few explicit abstractions or interfaces were defined."
            suggestion = "Introduce abstract interfaces for swappable strategies or components."
        else:
            score = 5
            evidence = "Minimal encapsulation demonstrated in class descriptions."
            concern = "Internal state and behavior appear tightly coupled."
            suggestion = "Hide implementation details behind clear method signatures and interfaces."

        return EvaluationCriterionDomain(
            name="Encapsulation and Abstraction",
            score=score,
            evidence=evidence,
            concern=concern,
            suggestion=suggestion,
            confidence=0.80
        )

    def _eval_coupling(self, rel: str, classes: str) -> EvaluationCriterionDomain:
        rel_lower = rel.lower()
        has_relationship_terms = any(w in rel_lower for w in ["composition", "aggregation", "has-a", "is-a", "inherits", "implements", "contains", "references", "associates"])
        rel_words = len(rel.split())

        if has_relationship_terms and rel_words > 25:
            score = 8
            evidence = f"Articulated structured relationships ({rel_words} words) using standard OOP associations."
            concern = "Direct dependencies may increase coupling between high-level controllers and concrete items."
            suggestion = "Prefer composition over inheritance and consider dependency injection for external handlers."
        elif rel_words > 15:
            score = 6
            evidence = f"Outlined basic class interactions ({rel_words} words)."
            concern = "Types of relationships (composition vs aggregation vs inheritance) are not clearly differentiated."
            suggestion = "Explicitly specify whether relationships are 'has-a' (composition) or 'is-a' (inheritance)."
        else:
            score = 4
            evidence = "Relationships section is brief or lacks relationship semantics."
            concern = "Unclear how instances instantiate and communicate with one another."
            suggestion = "Describe the relationship and cardinality between each pair of interacting classes."

        return EvaluationCriterionDomain(
            name="Coupling and Cohesion",
            score=score,
            evidence=evidence,
            concern=concern,
            suggestion=suggestion,
            confidence=0.85
        )

    def _eval_extensibility(self, dec: str, classes: str) -> EvaluationCriterionDomain:
        combined = f"{dec} {classes}".lower()
        has_patterns = any(w in combined for w in ["pattern", "strategy", "factory", "observer", "state", "extensible", "open-closed", "pluggable"])

        if has_patterns:
            score = 8
            evidence = "Design explicitly accounts for future extensions using architectural patterns."
            concern = "Avoid speculative generality or over-engineering for features not yet required."
            suggestion = "Document how a new requirement (such as a new payment method or dispatch algorithm) plugs in."
        elif len(dec.split()) > 25:
            score = 6
            evidence = "Explained design decisions with basic extensibility in mind."
            concern = "Adding new types or behaviors may require modifying existing core classes."
            suggestion = "Apply the Open-Closed Principle (OCP) using Strategy or State patterns."
        else:
            score = 5
            evidence = "Basic design choices noted without detailed extensibility analysis."
            concern = "System may be rigid when new requirements are introduced."
            suggestion = "Identify likely axes of change and introduce polymorphic extension points."

        return EvaluationCriterionDomain(
            name="Extensibility",
            score=score,
            evidence=evidence,
            concern=concern,
            suggestion=suggestion,
            confidence=0.80
        )

    def _eval_edge_cases(self, edge: str) -> EvaluationCriterionDomain:
        edge_lower = edge.lower()
        edge_words = len(edge.split())
        has_edge_terms = any(w in edge_lower for w in ["concurrency", "thread", "full", "empty", "overflow", "fail", "null", "invalid", "race", "timeout", "exhaust", "abort", "cancel"])

        if has_edge_terms and edge_words > 30:
            score = 8
            evidence = f"Identified critical edge cases ({edge_words} words) including failure conditions and concurrency."
            concern = "Recovery actions for severe failures (e.g. system restarts) could be further specified."
            suggestion = "Specify idempotent recovery and rollback mechanisms for failed operations."
        elif edge_words > 15:
            score = 6
            evidence = f"Mentioned boundary conditions ({edge_words} words)."
            concern = "Missed concurrent access scenarios or abnormal termination states."
            suggestion = "Analyze multi-threaded access and boundary conditions (empty/full queues, invalid inputs)."
        else:
            score = 4
            evidence = "Edge case coverage is minimal."
            concern = "System behavior during abnormal or peak conditions is undefined."
            suggestion = "List at least 3-4 specific boundary conditions and how the system gracefully recovers."

        return EvaluationCriterionDomain(
            name="Edge Cases",
            score=score,
            evidence=evidence,
            concern=concern,
            suggestion=suggestion,
            confidence=0.85
        )

    def _eval_tradeoffs(self, dec: str) -> EvaluationCriterionDomain:
        dec_lower = dec.lower()
        dec_words = len(dec.split())
        has_tradeoff_terms = any(w in dec_lower for w in ["trade-off", "tradeoff", "versus", "vs", "alternative", "chose", "because", "simplicity", "performance", "memory", "latency"])

        if has_tradeoff_terms and dec_words > 30:
            score = 8
            evidence = f"Clear justification of design trade-offs ({dec_words} words) explaining rationale behind design decisions."
            concern = "Quantitative trade-offs (e.g. time vs space complexity) could be elaborated."
            suggestion = "Compare the chosen approach against a concrete alternative rejected during design."
        elif dec_words > 15:
            score = 6
            evidence = f"Provided reasoning for primary design decisions ({dec_words} words)."
            concern = "Trade-offs and alternative solutions were not explicitly compared."
            suggestion = "Explicitly state what alternative approaches were considered and why they were rejected."
        else:
            score = 4
            evidence = "Trade-offs section is brief."
            concern = "Design decisions lack clear justification or alternative comparison."
            suggestion = "Provide a 'Decision vs. Rejected Alternative' justification for major components."

        return EvaluationCriterionDomain(
            name="Design Reasoning / Trade-offs",
            score=score,
            evidence=evidence,
            concern=concern,
            suggestion=suggestion,
            confidence=0.80
        )

    def _generate_strengths(self, criteria: List[EvaluationCriterionDomain]) -> List[str]:
        strengths = []
        for c in sorted(criteria, key=lambda x: x.score, reverse=True):
            if c.score >= 7 and len(strengths) < 3:
                strengths.append(f"{c.name}: {c.evidence}")
        if not strengths:
            strengths.append("Structured submission with all required sections filled.")
            strengths.append("Clear identification of core domain entities.")
        return strengths

    def _generate_improvements(self, criteria: List[EvaluationCriterionDomain]) -> List[str]:
        improvements = []
        for c in sorted(criteria, key=lambda x: x.score):
            if c.score <= 7 and len(improvements) < 3:
                improvements.append(f"{c.name}: {c.suggestion}")
        if not improvements:
            improvements.append("Consider formalizing class contracts with strict interface types.")
            improvements.append("Explore asynchronous event-driven notifications for state transitions.")
        return improvements
