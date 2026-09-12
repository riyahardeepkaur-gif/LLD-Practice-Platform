# Research Note: Modernizing Low-Level Design (LLD) Practice & Evaluation

## 1. Executive Summary & The Learner Problem
In modern software engineering assessments—particularly for SDE-2, SDE-3, and Senior Engineering roles across top technology organizations—**Low-Level Design (LLD) / Object-Oriented Design (OOD)** interviews serve as a critical filter for evaluating code craft, modular thinking, architectural hygiene, and extensibility. 

Unlike Data Structures & Algorithms (DSA), which offer binary test assertions (pass/fail against leetcode test cases), or High-Level System Design (HLD), which focuses on distributed scaling, caching, and database partitioning, LLD evaluates:
- Domain modeling (identifying entities, value objects, and aggregates)
- Application of SOLID design principles
- Appropriate decoupling via design patterns (e.g., Strategy, Factory, State, Observer)
- Separation of concerns and single-responsibility boundaries
- Concurrency and boundary case handling

**The Learner Problem**: Despite the importance of LLD, learners face an acute pedagogical bottleneck. When preparing for LLD, candidates typically read static blog posts or watch retrospective YouTube solutions. When attempting to practice on their own, there is **no interactive feedback loop**. A learner designs a parking lot or elevator system on a piece of paper or Google Doc, but cannot objectively answer:
- *Did I assign too many responsibilities to the central manager?*
- *Did I expose internal mutable state instead of encapsulating it?*
- *Is my spot allocation algorithm decoupled enough to swap strategies later?*
- *What edge cases did I miss before an interviewer points them out?*

---

## 2. How LLD Practice Is Commonly Done Today
Currently, software engineers rely on a fragmented mix of three primary mediums:

1. **Static Video & Blog Walkthroughs** (e.g., Gaurav Sen's System Design, Concept Coding, GeeksforGeeks):
   - *Workflow*: The learner passively watches an instructor draw UML or write Java classes for a classic problem.
   - *Limitation*: Highly passive; creates an "illusion of competence" where learners recognize solutions without being able to synthesize designs from scratch.

2. **Peer Mock Interviews** (e.g., Pramp, Interviewing.io):
   - *Workflow*: Candidates schedule live 1-on-1 sessions to practice design problems with peers or paid mentors.
   - *Limitation*: High scheduling friction, unpredictable peer interviewer quality, mentor fatigue, and high monetary cost ($100–$250/session on premium platforms).

3. **Ad-Hoc LLM Prompting** (e.g., pasting drafts into raw ChatGPT / Claude web chats):
   - *Workflow*: Learners paste raw bullet points into general-purpose chatbots asking "Is this design good?".
   - *Limitation*: Prompt drift, sycophantic responses ("Great design!"), lack of rubric consistency, and zero structured persistence across multiple iterative attempts.

---

## 3. Review of Existing Tools & Approaches

| Platform / Approach | Primary Strengths | Critical Gaps in LLD Practice |
| :--- | :--- | :--- |
| **LeetCode / HackerRank** | Automated judge, instantaneous grading, clear test suites. | Strictly DSA / algorithmic execution. No architectural rubric, no evaluation of class modularity, coupling, or SOLID principles. |
| **Educative.io (Grokking the LLD Interview)** | High-quality text explanations, clean UML diagrams, curated problem lists. | Entirely static reading material. No interactive submission portal, no personalized feedback on the learner's own design attempts. |
| **Interviewing.io / Pramp** | Realistic human interview conditions, rich behavioral feedback. | Expensive, difficult to schedule, unstandardized rubrics, non-repeatable for quick daily practice loops. |
| **Eraser.io / Excalidraw** | Excellent freeform diagramming and architectural sketching. | Canvas-only tooling with no domain evaluation engine or structured rubrics. |

---

## 4. Product Opportunity: The Focused Practice Loop
There is a clear white space for a dedicated, deliberate-practice LLD platform that mimics the LeetCode loop for Low-Level Design:

$$\text{Select Problem} \longrightarrow \text{Structure Design} \longrightarrow \text{Submit} \longrightarrow \text{Explainable Rubric Feedback} \longrightarrow \text{Iterate \& Retry}$$

To make this effective, the platform must deliver:
1. **Low Friction**: No complex IDE setups, compilers, or heavy UML canvas overhead.
2. **Objective, Explainable Feedback**: Scores tied directly to concrete quotes from the candidate's design, highlighting explicit weaknesses and suggestions.
3. **Iterative History**: Visibility into Attempt #1 vs Attempt #2 to demonstrate tangible design improvement.

---

## 5. Architectural Choices in Our MVP

### Why Structured Text-Based Submission?
In this MVP, we deliberately chose a **6-part structured text submission format**:
1. *Requirements & Assumptions*
2. *Classes*
3. *Responsibilities*
4. *Relationships*
5. *Design Decisions & Trade-offs*
6. *Edge Cases*

**Pedagogical Rationale**:
- **Cognitive Load Reduction**: Asking learners to draw pixel-perfect UML diagrams or write 500 lines of boilerplate Java/C++ in a 2-day assignment distracts from the core architectural thinking: *cohesion, coupling, encapsulation, and trade-offs*.
- **Interview Realism**: In real tech interviews, candidates spend the first 20 minutes outlining assumptions, listing primary entities, and defending trade-offs before writing any code.
- **Machine Comprehensibility**: Structured sections allow deterministic validation (preventing empty sections) and precise rubric alignment during automated evaluation.

### Why Combine Deterministic Checks and AI Evaluation?
A common failure mode of AI-powered applications is over-reliance on the LLM for basic validation. We decouple the evaluation pipeline into two complementary tiers:

1. **Deterministic Guardrails & Fallback Evaluator (`RuleBasedEvaluator`)**:
   - Performs objective structural checks (presence of all sections, character thresholds, domain keyword coverage, OOP relationship keywords).
   - Guarantees that the entire application runs, evaluates, and tests **100% offline without requiring external API keys or paid credits**.
   - Preserves candidate submissions unconditionally; even if an external evaluator times out, the submission is securely saved in SQLite with status `FAILED` and can be retried.

2. **AI Judgment Evaluator (`AIEvaluator`)**:
   - Focuses on qualitative assessment: *Did the student violate Single Responsibility in `ParkingLot`? Is the LOOK elevator dispatch algorithm appropriate here?*
   - Prompts for strictly formatted JSON conforming to a 7-criteria rubric.
   - Includes confidence scores and quotes student text as evidence, eliminating vague or hallucinated feedback.

---

## 6. References & Citations
1. Martin, Robert C. *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall, 2017.
2. Gamma, E., Helm, R., Johnson, R., & Vlissides, J. *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley, 1994.
3. Fowler, Martin. *Refactoring: Improving the Design of Existing Code*. Addison-Wesley Professional, 2nd Edition, 2018.
4. Educative, Inc. *Grokking the Low Level Design Interview Using OOD Principles*. [https://www.educative.io/courses/grokking-the-low-level-design-interview-using-ood-principles](https://www.educative.io/courses/grokking-the-low-level-design-interview-using-ood-principles).
5. OpenAI. *Structured Outputs in the API*. [https://platform.openai.com/docs/guides/structured-outputs](https://platform.openai.com/docs/guides/structured-outputs).
