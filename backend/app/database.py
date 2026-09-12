from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.entities import (
    Base,
    ProblemModel,
    AttemptModel,
    SubmissionModel,
    EvaluationModel,
    EvaluationCriterionModel,
    utcnow
)

# SQLite connection args for concurrent access in development
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


INITIAL_PROBLEMS = [
    {
        "slug": "parking-lot",
        "title": "Parking Lot",
        "difficulty": "Medium",
        "description": "Design a parking management system supporting multiple vehicle types, parking spaces across multiple floors, and dynamic fee calculation.",
        "functional_requirements": [
            "Support multiple floors and distinct spot types (Motorcycle, Compact, Large/Bus).",
            "Support multiple vehicle types mapped to compatible spot types.",
            "Issue an entry ticket with a unique ID, allocated spot, and entry timestamp.",
            "Dynamically find and assign available parking spots based on an allocation strategy (e.g. nearest to entrance).",
            "Calculate parking fees at exit based on vehicle type and duration parked.",
            "Display available spot counters per floor and vehicle type in real time."
        ],
        "considerations": [
            "Concurrency handling when multiple vehicles enter simultaneously at different gates.",
            "Separation of concerns: parking spot allocation strategy vs. payment calculation vs. ticket management.",
            "Extensibility for new vehicle types (e.g., Electric Vehicle with charging) and custom pricing schemes (e.g., peak hours).",
            "Handling full capacity and graceful failure when no spots match vehicle requirements."
        ],
        "evaluation_rubric": [
            {"name": "Requirement Understanding", "description": "Accurately captures vehicle types, spot assignment, ticketing, and fee calculation."},
            {"name": "Class Responsibilities", "description": "Single responsibility for ParkingLot, ParkingFloor, Spot, Vehicle, Ticket, Payment."},
            {"name": "Encapsulation and Abstraction", "description": "Proper interfaces for parking strategy and payment processor; avoids leaky internals."},
            {"name": "Coupling and Cohesion", "description": "Loose coupling between vehicle hierarchy and parking management."},
            {"name": "Extensibility", "description": "Easy to plug in new parking strategies, vehicle types, or rate cards without changing core classes."},
            {"name": "Edge Cases", "description": "Considers lot full, lost ticket, concurrent gate entries, oversized vehicles."},
            {"name": "Design Reasoning / Trade-offs", "description": "Justifies class relationships, design patterns used, and performance trade-offs."}
        ]
    },
    {
        "slug": "elevator-system",
        "title": "Elevator System",
        "difficulty": "Medium",
        "description": "Design an elevator control system for a multi-story building coordinating multiple elevator cars with optimal dispatch algorithms.",
        "functional_requirements": [
            "Control multiple elevator cars serving N floors in a commercial/residential building.",
            "Handle internal requests: passenger presses target floor button inside the car.",
            "Handle external requests: user presses Up or Down hall call button on a floor.",
            "Dispatch requests to appropriate elevator cars efficiently to minimize passenger wait and transit time.",
            "Maintain and transition elevator states (IDLE, MOVING_UP, MOVING_DOWN, DOOR_OPEN).",
            "Manage safety controls such as door obstruction sensors, weight limits, and emergency stop."
        ],
        "considerations": [
            "Dispatch algorithm selection (e.g., LOOK / SCAN vs. Nearest Car vs. Zone-based dispatch) and fairness.",
            "Decoupling the central ElevatorController / Dispatcher from individual ElevatorCar models.",
            "Concurrency control for simultaneous hall calls and internal requests across threads.",
            "Handling starvation where requests in opposite directions are indefinitely delayed."
        ],
        "evaluation_rubric": [
            {"name": "Requirement Understanding", "description": "Understands internal vs. external requests, state transitions, and dispatch coordination."},
            {"name": "Class Responsibilities", "description": "Separates ElevatorController, ElevatorCar, Request/Call, Door, DispatchStrategy."},
            {"name": "Encapsulation and Abstraction", "description": "Encapsulates car motion, door control, and scheduling strategies."},
            {"name": "Coupling and Cohesion", "description": "Central controller delegates movement and state management cleanly to cars."},
            {"name": "Extensibility", "description": "Enables pluggable scheduling algorithms (e.g. energy-saving mode, morning rush)."},
            {"name": "Edge Cases", "description": "Considers max capacity reached, power outage/emergency stop, idle repositioning."},
            {"name": "Design Reasoning / Trade-offs", "description": "Explains scheduling algorithm choice, state synchronization, and trade-offs."}
        ]
    },
    {
        "slug": "vending-machine",
        "title": "Vending Machine",
        "difficulty": "Easy/Medium",
        "description": "Design a vending machine supporting product selection, multi-denomination payments, change return, and reliable inventory management.",
        "functional_requirements": [
            "Manage lifecycle states: NoCoinState, HasCoinState, DispenseState, SoldOutState.",
            "Accept payment in various coin/note denominations and maintain current inserted balance.",
            "Allow user to select an available product code.",
            "Dispense product if inserted balance is sufficient and inventory is available.",
            "Calculate and return exact change using available cash reserves.",
            "Allow user to cancel transaction at any point before dispensing and receive a full refund of inserted funds."
        ],
        "considerations": [
            "Use of the State Design Pattern to avoid giant if/else or switch statements.",
            "Atomic operations: ensuring inventory is decremented and cash collected only upon successful dispense.",
            "Handling insufficient change scenario when cash register lacks exact change denominations.",
            "Concurrency and hardware safety simulation (e.g. coin return jammed, product shelf empty)."
        ],
        "evaluation_rubric": [
            {"name": "Requirement Understanding", "description": "Understands state transitions, payment balance, change calculation, and refund."},
            {"name": "Class Responsibilities", "description": "Clear boundaries between VendingMachine, State hierarchy, Inventory, Product, CashRegister."},
            {"name": "Encapsulation and Abstraction", "description": "State pattern implementation with a clear VendingMachineState interface."},
            {"name": "Coupling and Cohesion", "description": "Context delegates state-dependent actions cleanly to the active state."},
            {"name": "Extensibility", "description": "Easily support card/digital payments or new promotional states."},
            {"name": "Edge Cases", "description": "Considers exact change unavailable, item out of stock, refund mid-transaction."},
            {"name": "Design Reasoning / Trade-offs", "description": "Justifies State pattern vs. simple state enum, transaction atomicity decisions."}
        ]
    }
]


SAMPLE_ATTEMPT_DATA = {
    "problem_slug": "parking-lot",
    "attempt_number": 1,
    "status": "COMPLETED",
    "is_sample": True,
    "submission": {
        "requirements_assumptions": "Multi-floor parking lot system supporting motorcycle, car, and bus types. Dynamic hourly billing.",
        "classes": "ParkingLot, ParkingFloor, ParkingSpot, Vehicle, Motorcycle, Car, Bus, Ticket, PaymentService, AllocationStrategy",
        "responsibilities": "ParkingLot coordinates gates. ParkingFloor tracks spot states. Ticket stores entry timestamp. PaymentService calculates fees.",
        "relationships": "ParkingLot has-a list of ParkingFloor (composition). ParkingFloor has-a list of ParkingSpot. Vehicle is-a hierarchy.",
        "design_decisions": "Used Strategy Pattern for spot allocation algorithm. Separated fee calculation into PaymentStrategy for extensible pricing rules.",
        "edge_cases": "Full lot throws LotFullException. Synchronized lock on spots avoids race conditions during concurrent gate entry."
    },
    "evaluation": {
        "evaluator_type": "RULE_BASED",
        "overall_score": 51,
        "strengths": [
            "Extensibility: Design explicitly accounts for future extensions using architectural patterns."
        ],
        "improvements": [
            "Class Responsibilities: Break the domain down into at least 4-5 focused classes reflecting system entities.",
            "Coupling and Cohesion: Describe the relationship and cardinality between each pair of interacting classes.",
            "Edge Cases: List at least 3-4 specific boundary conditions and how the system gracefully recovers."
        ],
        "summary": "The submission demonstrates a solid functional grasp with an overall score of 51/100. 8 of 9 key domain concepts were identified. Focus on the recommended suggestions to refine modularity and trade-off depth.",
        "criteria": [
            {
                "name": "Requirement Understanding",
                "score": 5,
                "evidence": "Basic requirements provided (13 words).",
                "concern": "Requirements description is brief and omits critical domain constraints.",
                "suggestion": "Detail functional requirements including inputs, expected outputs, and scope limits.",
                "confidence": 0.85
            },
            {
                "name": "Class Responsibilities",
                "score": 4,
                "evidence": "Limited class decomposition (1 classes identified).",
                "concern": "Insufficient class breakdown makes it difficult to verify separation of concerns.",
                "suggestion": "Break the domain down into at least 4-5 focused classes reflecting system entities.",
                "confidence": 0.85
            },
            {
                "name": "Encapsulation and Abstraction",
                "score": 5,
                "evidence": "Minimal encapsulation demonstrated in class descriptions.",
                "concern": "Internal state and behavior appear tightly coupled.",
                "suggestion": "Hide implementation details behind clear method signatures and interfaces.",
                "confidence": 0.8
            },
            {
                "name": "Coupling and Cohesion",
                "score": 4,
                "evidence": "Relationships section is brief or lacks relationship semantics.",
                "concern": "Unclear how instances instantiate and communicate with one another.",
                "suggestion": "Describe the relationship and cardinality between each pair of interacting classes.",
                "confidence": 0.85
            },
            {
                "name": "Extensibility",
                "score": 8,
                "evidence": "Design explicitly accounts for future extensions using architectural patterns.",
                "concern": "Avoid speculative generality or over-engineering for features not yet required.",
                "suggestion": "Document how a new requirement (such as a new payment method or dispatch algorithm) plugs in.",
                "confidence": 0.8
            },
            {
                "name": "Edge Cases",
                "score": 4,
                "evidence": "Edge case coverage is minimal.",
                "concern": "System behavior during abnormal or peak conditions is undefined.",
                "suggestion": "List at least 3-4 specific boundary conditions and how the system gracefully recovers.",
                "confidence": 0.85
            },
            {
                "name": "Design Reasoning / Trade-offs",
                "score": 6,
                "evidence": "Provided reasoning for primary design decisions (16 words).",
                "concern": "Trade-offs and alternative solutions were not explicitly compared.",
                "suggestion": "Explicitly state what alternative approaches were considered and why they were rejected.",
                "confidence": 0.8
            }
        ]
    }
}


def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_columns()
    seed_problems()
    seed_sample_attempts()


def _migrate_columns():
    """Ensure newly added columns exist in development SQLite databases."""
    if "sqlite" in settings.database_url:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("PRAGMA table_info(attempts)"))
                columns = [row[1] for row in res.fetchall()]
                if "is_sample" not in columns:
                    conn.execute(text("ALTER TABLE attempts ADD COLUMN is_sample BOOLEAN DEFAULT 0 NOT NULL"))
                    conn.commit()
        except Exception:
            pass


def seed_problems():
    db = SessionLocal()
    try:
        for problem_data in INITIAL_PROBLEMS:
            existing = db.query(ProblemModel).filter_by(slug=problem_data["slug"]).first()
            if not existing:
                problem = ProblemModel(**problem_data)
                db.add(problem)
        db.commit()
    finally:
        db.close()


def seed_sample_attempts():
    """Retains exactly 1 completed reference attempt for demo/reference and cleans up unfinished sample attempts."""
    db = SessionLocal()
    try:
        # 1. Clean up unfinished dummy attempts (STARTED attempts with no submission)
        empty_started_attempts = (
            db.query(AttemptModel)
            .filter(AttemptModel.status == "STARTED", ~AttemptModel.submission.has())
            .all()
        )
        for att in empty_started_attempts:
            db.delete(att)
        db.commit()

        # 2. Check if a completed sample attempt already exists
        existing_sample = db.query(AttemptModel).filter(AttemptModel.is_sample.is_(True)).first()
        if existing_sample:
            return

        # 3. If Attempt #1 exists (e.g. from existing DB), ensure it is marked as is_sample=True
        attempt_one = db.query(AttemptModel).filter(AttemptModel.id == 1).first()
        if attempt_one and attempt_one.status == "COMPLETED":
            attempt_one.is_sample = True
            db.commit()
            return

        # 4. Otherwise, seed the reference completed sample attempt for Parking Lot
        prob = db.query(ProblemModel).filter_by(slug=SAMPLE_ATTEMPT_DATA["problem_slug"]).first()
        if not prob:
            return

        sample_attempt = AttemptModel(
            problem_id=prob.id,
            attempt_number=SAMPLE_ATTEMPT_DATA["attempt_number"],
            status=SAMPLE_ATTEMPT_DATA["status"],
            is_sample=True,
            created_at=utcnow(),
            updated_at=utcnow()
        )
        db.add(sample_attempt)
        db.flush()

        sub_data = SAMPLE_ATTEMPT_DATA["submission"]
        sub = SubmissionModel(
            attempt_id=sample_attempt.id,
            requirements_assumptions=sub_data["requirements_assumptions"],
            classes=sub_data["classes"],
            responsibilities=sub_data["responsibilities"],
            relationships=sub_data["relationships"],
            design_decisions=sub_data["design_decisions"],
            edge_cases=sub_data["edge_cases"],
            submitted_at=utcnow()
        )
        db.add(sub)
        db.flush()

        eval_data = SAMPLE_ATTEMPT_DATA["evaluation"]
        eval_model = EvaluationModel(
            attempt_id=sample_attempt.id,
            evaluator_type=eval_data["evaluator_type"],
            overall_score=eval_data["overall_score"],
            strengths=eval_data["strengths"],
            improvements=eval_data["improvements"],
            summary=eval_data["summary"],
            created_at=utcnow()
        )
        db.add(eval_model)
        db.flush()

        for c in eval_data["criteria"]:
            crit = EvaluationCriterionModel(
                evaluation_id=eval_model.id,
                name=c["name"],
                score=c["score"],
                evidence=c["evidence"],
                concern=c["concern"],
                suggestion=c["suggestion"],
                confidence=c["confidence"]
            )
            db.add(crit)

        db.commit()
    finally:
        db.close()
