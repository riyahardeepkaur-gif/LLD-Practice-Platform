# AI Assistance & Architectural Decision Log

This document transparently records meaningful AI-assisted decisions made during the design, architecture, and implementation of the **LLD Practice Platform**. Each decision highlights the problem context, initial AI proposals, our critical evaluation, modifications made, and the final engineering rationale.

---

## Decision 1: Submission Medium (Structured Text vs. Interactive UML Canvas)

### 1. What problem we were solving
We needed to decide how learners express their Low-Level Designs. In real interviews, candidates convey architecture using a mix of entity definitions, interface boundaries, and verbal trade-offs.

### 2. What AI suggested
The AI initially proposed building an interactive drag-and-drop UML canvas (using libraries like React Flow or HTML Canvas) that allows learners to visually draw class boxes, connect relationship arrows, and generate code templates.

### 3. What we accepted
We accepted the premise that visual representation is appealing in production platforms.

### 4. What we rejected or changed
We **rejected the interactive UML diagram editor** for the MVP. Instead, we designed a **6-section structured text submission format**:
1. *Requirements & Assumptions*
2. *Classes*
3. *Responsibilities*
4. *Relationships*
5. *Design Decisions & Trade-offs*
6. *Edge Cases*

### 5. Why we made the final decision
- **Scope & Cognitive Focus**: A UML canvas in a 2-day engineering assignment creates massive front-end accidental complexity (canvas state, geometry, arrow anchoring, drag-and-drop mobile quirks) without adding pedagogical value.
- **Pedagogical Purity**: An LLD assessment evaluates *modular reasoning, SRP adherence, decoupling, and trade-off justification*. A structured 6-field form forces the candidate to think through these exact dimensions without UI friction.
- **Machine Comprehensibility & Deterministic Checks**: Structured text fields enable robust deterministic validation (checking empty sections, length thresholds) and clear rubric mapping for automated evaluation.

---

## Decision 2: Evaluator Architecture & Extensibility (Strategy Pattern vs. Unified Evaluator)

### 1. What problem we were solving
We needed an evaluation engine capable of leveraging an LLM for nuanced qualitative feedback while remaining 100% testable, runnable, and demonstrable offline when no external API key is provided.

### 2. What AI suggested
The AI suggested creating a single `EvaluationService` class that contains internal `if/else` checks: if `OPENAI_API_KEY` is present, call OpenAI; otherwise, run mock heuristics inside private methods of the same service.

### 3. What we accepted
We accepted that the system must dynamically switch between AI and deterministic evaluation based on environment configuration.

### 4. What we rejected or changed
We **rejected embedding evaluation logic directly inside the service layer**. Instead, we implemented a formal **Strategy Pattern** with an abstract `BaseEvaluator` interface:
```
BaseEvaluator (ABC)
├── RuleBasedEvaluator (Deterministic heuristic scoring & rubric generation)
└── AIEvaluator (Structured LLM prompting with graceful fallback)
```
We also introduced an `EvaluatorFactory` to resolve the active strategy and added distinct `evaluator_type` tracking (`RULE_BASED`, `AI`, `AI_FALLBACK`).

### 5. Why we made the final decision
- **Separation of Concerns**: The `AttemptService` orchestrates attempt state transitions and persistence; it should not know *how* evaluation scores are calculated.
- **Change Test B Compliance**: If a human mentor review or static AST code linter is added later, a new class implementing `BaseEvaluator` can be plugged in without modifying a single line of the practice or submission flow.
- **Testability**: Pytest tests can inject custom test doubles (e.g. `FailingEvaluator`) into `AttemptService` without mocking HTTP network libraries.

---

## Decision 3: Fallback Evaluator Scope & Complexity

### 1. What problem we were solving
When running without an LLM API key, the platform must provide a realistic, explainable evaluation result so that another engineer can clone and evaluate the application end-to-end.

### 2. What AI suggested
The AI initially generated a complex NLP parser using regular expressions and AST parsers to simulate deep object-oriented reasoning (attempting to detect inheritance trees and calculate coupling metrics programmatically from free text).

### 3. What we accepted
We accepted that the fallback evaluator must output the exact same 7-criteria JSON schema (`overall_score`, `criteria` with evidence, concerns, suggestions, confidence, strengths, improvements) as the AI evaluator.

### 4. What we rejected or changed
We **rejected over-engineering the RuleBasedEvaluator with fragile pseudo-NLP**. Following the user's explicit scope refinement, we scoped `RuleBasedEvaluator` to practical, reliable deterministic checks:
- Verifying presence and minimum length of all 6 mandatory sections.
- Checking domain concept coverage per problem (e.g., `Spot`, `Vehicle`, `Ticket` for Parking Lot; `ElevatorController`, `Car`, `Request`, `Door` for Elevator; `State`, `Product`, `Coin`, `Dispense` for Vending Machine).
- Checking OOP relationship keywords (`composition`, `has-a`, `is-a`, `implements`).
- Checking edge case and concurrency keywords (`race`, `deadlock`, `full`, `capacity`, `null`, `recovery`).
- Checking trade-off keywords (`trade-off`, `versus`, `chose`, `because`).

### 5. Why we made the final decision
- Simulating human-level LLD reasoning with regex is fundamentally fragile and misaligned with deterministic evaluation.
- The deterministic checks provide fast (<50ms), reliable, reproducible scores and actionable suggestions while preserving clear separation between rule-based guardrails and AI qualitative judgment.

---

## Decision 4: Asynchronous Evaluation & Infrastructure (In-Process vs. Distributed Task Queue)

### 1. What problem we were solving
Evaluation involves network latency (or computation) after the learner clicks "Submit". We needed to decide how to execute and surface the evaluation process.

### 2. What AI suggested
The AI suggested setting up Celery with a Redis broker or a RabbitMQ container to process evaluations asynchronously as background worker jobs.

### 3. What we accepted
We accepted the requirement that submission state must transition from `SUBMITTED` &rarr; `EVALUATING` &rarr; `COMPLETED` (or `FAILED`), and that the UI should display an evaluating state.

### 4. What we rejected or changed
We **strictly rejected Redis, Celery, RabbitMQ, and external brokers**. Instead, we implemented evaluation as an asynchronous service call within FastAPI (`async def submit_and_evaluate`) with explicit SQLite database state updates.

### 5. Why we made the final decision
- **Assignment Scope**: The assignment explicitly forbids microservices, message brokers, Docker orchestration, and unnecessary infrastructure.
- **Performance**: In-process async execution completes in <1s for rule-based evaluation and 2–4s for LLM evaluation. Adding a distributed message broker would add operational fragility, multiple running processes, and setup hurdles with zero tangible user benefit for an MVP.

---

## Decision 5: Submission Safety & State Persistence Under Failure

### 1. What problem we were solving
External AI APIs frequently suffer from rate limits, network timeouts, or malformed JSON responses. We needed to ensure learner work is never lost.

### 2. What AI suggested
The AI suggested catching exceptions in the API controller and returning an HTTP 500 error to the client, asking the user to click submit again.

### 3. What we accepted
We accepted that external LLM calls can fail unpredictably.

### 4. What we rejected or changed
We **rejected discarding state on error**. Instead, we designed a persistent transactional sequence:
1. When the user submits, the submission is immediately written to the database and the attempt status is set to `SUBMITTED`.
2. The attempt status transitions to `EVALUATING`.
3. If an unhandled failure occurs, the attempt status transitions to `FAILED`.
4. The submission text is completely preserved in SQLite. The learner can review their submitted text and retry the evaluation without retyping their design.

### 5. Why we made the final decision
- Learner trust is paramount. Losing 15 minutes of architectural drafting due to an API timeout is unacceptable.
- Preserving the submission in SQLite decoupled data persistence from the evaluation outcome.
