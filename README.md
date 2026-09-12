# LLD Practice Platform (MVP)

A focused, deliberate-practice platform for **Low-Level Design (LLD)** and **Object-Oriented Design (OOD)**. 

The platform empowers software engineers to practice classic system design problems, submit structured architectural decisions across 6 critical dimensions, and receive explainable, rubric-based feedback with grounded evidence, identified risks, and actionable suggestions.

---

## 1. Features

- **Problem Catalog**: Pre-seeded with 3 classic LLD problems:
  - **Parking Lot** (Medium): Multi-floor, multiple vehicle types, spot allocation algorithms, and fee calculation.
  - **Elevator System** (Medium): Multi-car dispatch algorithms (LOOK/SCAN), passenger requests, and state management.
  - **Vending Machine** (Easy/Medium): State Pattern lifecycle, cash/coin register, item dispensing, and refund handling.
- **Problem Detail View**: Clear breakdown of functional requirements, architectural considerations, and evaluation rubrics.
- **Structured 6-Part Submission Workspace**:
  1. *Requirements & Assumptions*
  2. *Classes & Enums*
  3. *Class Responsibilities*
  4. *Relationships & Associations*
  5. *Design Decisions & Trade-offs*
  6. *Edge Cases & Concurrency*
- **Explainable 7-Criteria Rubric Feedback**:
  1. *Requirement Understanding*
  2. *Class Responsibilities*
  3. *Encapsulation & Abstraction*
  4. *Coupling & Cohesion*
  5. *Extensibility*
  6. *Edge Cases*
  7. *Design Reasoning / Trade-offs*
  *(Each criterion provides score/10, quoted evidence, concerns, suggestions, and confidence rating)*.
- **Dual Evaluation Engine**:
  - **AI Evaluator**: Uses OpenAI-compatible LLMs with structured JSON prompting for nuanced qualitative critique.
  - **Deterministic Fallback Evaluator**: Runs 100% offline with zero external dependencies, computing rubric scores from domain entity coverage, OOP relationships, and architectural trade-off discussion.
- **Submission Preservation Guarantee**: Submissions are persisted *before* evaluation. Even if an evaluation times out or errors, the learner's design is never lost.
- **Attempt History & Retries**: Track iterative score improvement across sequential attempts (`Attempt #1` &rarr; `Attempt #2`) with direct retry workflows.

---

## 2. Tech Stack

### Backend
- **Python 3.13**
- **FastAPI**: Modern, high-performance web framework
- **Pydantic v2**: Request/response validation and settings management
- **SQLAlchemy 2.0**: Relational database ORM
- **SQLite**: Zero-configuration embedded database
- **Pytest & pytest-asyncio**: Automated test suite

### Frontend
- **React 18** + **TypeScript**
- **Vite**: Ultra-fast build tool and dev server
- **React Router v6**: Client-side SPA navigation
- **Lucide React**: Clean developer-tool icons
- **Vanilla CSS**: Curated dark theme and design tokens

---

## 3. Project Structure

```
cypherschool/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI route handlers (problems, attempts)
│   │   ├── domain/          # Pure business models and domain exceptions
│   │   ├── evaluators/      # Strategy Pattern (Base, RuleBased, AI, Factory)
│   │   ├── models/          # SQLAlchemy database entities
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── repositories/    # Data persistence layer
│   │   ├── services/        # Orchestration and state transitions
│   │   ├── database.py      # SQLite connection & seed data
│   │   ├── config.py        # Pydantic settings & environment configuration
│   │   └── main.py          # FastAPI application & lifespan startup
│   ├── tests/               # Pytest automated test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (Navbar, Badge)
│   │   ├── pages/           # Route views (Home, Detail, Practice, Feedback, History)
│   │   ├── services/        # API client layer (fetch)
│   │   ├── types/           # TypeScript schema definitions
│   │   ├── App.tsx          # Router layout
│   │   ├── index.css        # Design tokens & styling
│   │   └── main.tsx         # React root
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/
│   ├── research-note.md     # Research on LLD learning & existing gaps
│   └── design-note.md       # Architecture, Mermaid diagrams, Change Tests A & B
├── README.md                # Project documentation
├── AI_USAGE.md              # 5 meaningful AI-assisted decisions & trade-offs
└── .env.example
```

---

## 4. Setup & Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

---

### Step 1: Backend Setup

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (optional):
   ```bash
   cp .env.example .env
   ```
   *If `LLM_API_KEY` is left blank, the application automatically uses the deterministic `RuleBasedEvaluator`.*

5. Run the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### Step 2: Frontend Setup

1. Open another terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   - Open your browser at [http://localhost:5173](http://localhost:5173)

---

### Step 3: Running Tests

Run the full automated test suite:
```bash
cd backend
python -m pytest tests -v
```

The test suite validates:
- Problem retrieval and database seeding
- Sequential attempt numbering (`#1`, `#2`)
- Input validation (empty/short submission rejection with 422)
- Valid submission persistence and state transitions (`SUBMITTED` &rarr; `EVALUATING` &rarr; `COMPLETED`)
- RuleBasedEvaluator rubric generation (evidence, concerns, suggestions)
- AIEvaluator fallback behavior when no API key is provided
- Evaluation failure handling (submission text is preserved under failure)
- Re-submission protection on completed attempts

---

## 5. How AI & Fallback Evaluation Works

```
                        [ Student Submission ]
                                  │
                                  ▼
                        [ Evaluator Factory ]
                                  │
                   Is LLM_API_KEY configured?
                                 / \
                           YES  /   \  NO
                               /     \
                              ▼       ▼
                       [AIEvaluator]  [RuleBasedEvaluator]
                              │
                    Did LLM succeed?
                          /   \
                    YES  /     \  NO (Timeout / Invalid JSON)
                        /       \
                       ▼         ▼
                EvaluatorType:  EvaluatorType:
                     "AI"       "AI_FALLBACK"
```

1. **AI Evaluator (`AIEvaluator`)**:
   - Prompts an OpenAI-compatible API with the student's submission, problem requirements, and 7-criteria rubric.
   - Enforces a strict JSON output schema.
   - If the API times out, returns HTTP errors, or produces malformed JSON, it gracefully delegates to `RuleBasedEvaluator` and records `evaluator_type = AI_FALLBACK`.

2. **Deterministic Fallback Evaluator (`RuleBasedEvaluator`)**:
   - Analyzes section presence, minimum word counts, domain concept coverage, OOP relationship keywords (`composition`, `implements`), and trade-off terms.
   - Populates evidence quotes, concerns, actionable suggestions, and confidence ratings for all 7 criteria.
   - Produces identical JSON structure, ensuring the application is fully demonstrable offline.

---

## 6. Example Practice Workflow

1. Navigate to **Problems** and choose **Parking Lot**.
2. Review the functional requirements (multiple floors, vehicle sizes, ticket issuance, fee calculation).
3. Click **Start Practice** &rarr; Generates `Attempt #1`.
4. Enter your design across the 6 structured fields.
5. Click **Submit Design**:
   - State transitions: `SUBMITTED` &rarr; `EVALUATING` &rarr; `COMPLETED`.
6. Review your **Feedback**:
   - Overall Score (e.g. `78/100`).
   - Evaluator badge (`AI Evaluator` or `Rule-Based Evaluator`).
   - Strengths and Priority Improvements.
   - 7 rubric criteria with concrete evidence and suggestions.
7. Click **Retry Problem**:
   - Initializes `Attempt #2`.
   - Incorporate the suggested improvements (e.g. separating parking allocation strategy from payment processing).
   - Submit and verify improved score in **Attempt History**.

---

## 7. Limitations & Future Improvements

### Current MVP Limitations:
- **Text-Only Submissions**: UML class diagrams must be described textually or via code-like syntax.
- **Local Storage**: Designed for local development and demonstration; no multi-user authentication.
- **Synchronous In-Process Evaluation**: Evaluation runs within the FastAPI async lifecycle without a background worker queue.

### Future Roadmap:
- **Class Diagram Support**: Accept Mermaid.js UML class diagrams alongside structured text.
- **Interactive Code Templates**: Generate starter skeletons in Java, Python, or TypeScript from the candidate's proposed classes.
- **Human Peer Review**: Support mentor feedback alongside AI and rule-based evaluation.
- **User Authentication**: Add user accounts, profiles, and saved drafts.
