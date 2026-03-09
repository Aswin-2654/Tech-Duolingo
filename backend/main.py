from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from passlib.context import CryptContext
from datetime import datetime, timedelta
 
import random
import hashlib
 
# ---------- DATABASE ----------
DATABASE_URL = "sqlite:///./tech_vocab.db"
 
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 
# ---------- PASSWORDS ----------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
def hash_password(password: str) -> str:
    # Normalize to a stable ASCII input before bcrypt to avoid backend byte-limit quirks.
    normalized = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(normalized)
 
def verify_password(password: str, hashed: str) -> bool:
    normalized = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.verify(normalized, hashed)
 
# ---------- MODELS ----------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    attempts = relationship("Attempt", back_populates="user")
 
 
class Term(Base):
    __tablename__ = "terms"
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True)
    short_definition = Column(String)
    detailed_explanation = Column(String)
    example_code_snippet = Column(String)
    real_world_example = Column(String)
    difficulty = Column(String, default="easy")
    attempts = relationship("Attempt", back_populates="term")
 
 
class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    term_id = Column(Integer, ForeignKey("terms.id"))
    is_correct = Column(Boolean, default=False)
 
    user = relationship("User", back_populates="attempts")
    term = relationship("Term", back_populates="attempts")
 
 
Base.metadata.create_all(bind=engine)
 
# ---------- SCHEMAS (PYDANTIC v2) ----------
class UserSignUp(BaseModel):
    name: str
    email: str
    password: str
 
 
class UserSignIn(BaseModel):
    email: str
    password: str
 
 
class UserRead(BaseModel):
    id: int
    name: str
    email: str
 
    model_config = ConfigDict(from_attributes=True)
 
 
class TermBase(BaseModel):
    term: str
    short_definition: str
    detailed_explanation: str
    example_code_snippet: str
    real_world_example: str
    difficulty: str = "easy"
 
 
class TermRead(TermBase):
    id: int
 
    model_config = ConfigDict(from_attributes=True)
 
 
class QuestionRequest(BaseModel):
    mode: Optional[str] = "definition"  # definition | code | example
 
 
class QuestionOption(BaseModel):
    term_id: int
    term: str
 
 
class QuestionResponse(BaseModel):
    term_id: int
    clue_type: str
    clue_text: str
    options: List[QuestionOption]
    hint: str
 
 
class AnswerRequest(BaseModel):
    term_id: int
    selected_term_id: int
 
 
class AnswerResponse(BaseModel):
    correct: bool
    message: str
    new_score: int
    explanation: str
 
 
class StatsResponse(BaseModel):
    user_id: int
    total_questions: int
    correct_answers: int
    accuracy: float
    total_points: int
 
 
class SignInResponse(BaseModel):
    user: UserRead
    token: str
 
 
# ---------- APP ----------
app = FastAPI(title="Tech Vocabulary Builder API")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)
 
 
 
# ---------- UTILS ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
 
def seed_terms(db):
    if db.query(Term).count() > 0:
        return
   
    sample_terms = [
        Term(term="API", short_definition="Application Programming Interface.", detailed_explanation="Defines how software components communicate.", example_code_snippet="GET /users", real_world_example="REST API endpoints.", difficulty="easy"),
        Term(term="JWT", short_definition="JSON Web Token for authentication.", detailed_explanation="Stateless token containing user claims.", example_code_snippet="Authorization: Bearer eyJ...", real_world_example="Login tokens.", difficulty="medium"),
        Term(term="Docker", short_definition="Containerization platform.", detailed_explanation="Packages apps with dependencies.", example_code_snippet="docker run -p 80:80 app", real_world_example="Microservices deployment.", difficulty="medium"),
        Term(term="REST", short_definition="Representational State Transfer.", detailed_explanation="HTTP-based API design standard.", example_code_snippet="GET /posts/123", real_world_example="Web APIs.", difficulty="easy"),
        Term(term="OAuth", short_definition="Authorization framework.", detailed_explanation="Delegated access without passwords.", example_code_snippet="Login with Google", real_world_example="Third-party logins.", difficulty="medium"),
        Term(term="Kubernetes", short_definition="Container orchestration.", detailed_explanation="Manages container clusters.", example_code_snippet="kubectl apply -f deploy.yaml", real_world_example="Cloud container management.", difficulty="hard"),
        Term(term="Microservices", short_definition="Small independent services.", detailed_explanation="Modular architecture pattern.", example_code_snippet="service-a → gRPC → service-b", real_world_example="Netflix architecture.", difficulty="hard"),
        Term(term="GraphQL", short_definition="Query language for APIs.", detailed_explanation="Precise data fetching.", example_code_snippet="{ user(id:1) { name } }", real_world_example="Facebook API.", difficulty="medium"),
        Term(term="CI/CD", short_definition="Continuous Integration/Deployment.", detailed_explanation="Automated pipelines.", example_code_snippet="git push → deploy", real_world_example="GitHub Actions.", difficulty="medium"),
        Term(term="ORM", short_definition="Object Relational Mapper.", detailed_explanation="Database as objects.", example_code_snippet="User.query.filter_by(id=1)", real_world_example="SQLAlchemy.", difficulty="easy"),
        Term(term="Webhook", short_definition="Event-driven HTTP callback.", detailed_explanation="Real-time notifications.", example_code_snippet="POST /webhook", real_world_example="GitHub notifications.", difficulty="medium"),
        Term(term="Cache", short_definition="Fast data storage.", detailed_explanation="Reduce database load.", example_code_snippet="@lru_cache", real_world_example="Redis.", difficulty="easy"),
        Term(term="Index", short_definition="Database query accelerator.", detailed_explanation="Faster lookups.", example_code_snippet="CREATE INDEX ON users(email)", real_world_example="Database optimization.", difficulty="easy"),
        Term(term="Load Balancer", short_definition="Distributes traffic.", detailed_explanation="High availability.", example_code_snippet="nginx upstream", real_world_example="AWS ELB.", difficulty="medium"),
        Term(term="MongoDB", short_definition="NoSQL document database.", detailed_explanation="JSON-like documents.", example_code_snippet="{ name: 'John', age: 30 }", real_world_example="Flexible schemas.", difficulty="easy"),
        Term(term="PostgreSQL", short_definition="Advanced relational database.", detailed_explanation="ACID compliant.", example_code_snippet="SELECT * FROM users WHERE active=true", real_world_example="Enterprise apps.", difficulty="medium"),
        Term(term="Redis", short_definition="In-memory data store.", detailed_explanation="Caching and sessions.", example_code_snippet="SET user:1 '{name:'John}'", real_world_example="Session storage.", difficulty="medium"),
        Term(term="gRPC", short_definition="High-performance RPC framework.", detailed_explanation="Protocol buffers.", example_code_snippet=".proto files", real_world_example="Microservices comms.", difficulty="hard"),
        Term(term="Terraform", short_definition="Infrastructure as code.", detailed_explanation="Cloud provisioning.", example_code_snippet="terraform apply", real_world_example="AWS/GCP infra.", difficulty="hard"),
        Term(term="Ansible", short_definition="Configuration management.", detailed_explanation="Agentless automation.", example_code_snippet="ansible-playbook site.yml", real_world_example="Server setup.", difficulty="medium"),
        Term(term="Prometheus", short_definition="Monitoring and alerting.", detailed_explanation="Time-series metrics.", example_code_snippet="metric{app='web'}=42", real_world_example="Kubernetes monitoring.", difficulty="hard"),
        Term(term="ELK Stack", short_definition="Logging pipeline.", detailed_explanation="Elasticsearch+Logstash+Kibana.", example_code_snippet="logs → Elasticsearch", real_world_example="Centralized logging.", difficulty="hard"),
        Term(term="Serverless", short_definition="Event-driven compute.", detailed_explanation="No server management.", example_code_snippet="AWS Lambda", real_world_example="FaaS functions.", difficulty="medium"),
        Term(term="CQRS", short_definition="Command Query Responsibility Segregation.", detailed_explanation="Separate read/write models.", example_code_snippet="separate read/write DBs", real_world_example="High-scale apps.", difficulty="hard"),
        Term(term="Event Sourcing", short_definition="Store state as event sequence.", detailed_explanation="Immutable event log.", example_code_snippet="events → current state", real_world_example="Audit trails.", difficulty="hard"),
    ]
    db.add_all(sample_terms)
    db.commit()
 
 
 
with SessionLocal() as db:
    seed_terms(db)
 
# ---------- SIMPLE AUTH ----------
def get_current_user(
    x_user_id: Optional[int] = Header(default=None), db=Depends(get_db)
):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
 
 
# ---------- AUTH ROUTES ----------
@app.post("/auth/signup", response_model=UserRead)
def sign_up(payload: UserSignUp, db=Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
 
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email}
 
 
@app.post("/auth/signin", response_model=SignInResponse)
def sign_in(payload: UserSignIn, db=Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
 
    return {
        "user": {"id": user.id, "name": user.name, "email": user.email},
        "token": str(user.id),
    }
 
 
# ---------- TERMS ----------
@app.get("/terms", response_model=List[TermRead])
def list_terms(
    difficulty: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    q = db.query(Term)
    if difficulty:
        q = q.filter(Term.difficulty == difficulty)
    terms = q.all()
    return [
        {
            "id": t.id,
            "term": t.term,
            "short_definition": t.short_definition,
            "detailed_explanation": t.detailed_explanation,
            "example_code_snippet": t.example_code_snippet,
            "real_world_example": t.real_world_example,
            "difficulty": t.difficulty,
        }
        for t in terms
    ]
 
 
@app.get("/terms/{term_id}", response_model=TermRead)
def get_term(
    term_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    term = db.query(Term).filter(Term.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return {
        "id": term.id,
        "term": term.term,
        "short_definition": term.short_definition,
        "detailed_explanation": term.detailed_explanation,
        "example_code_snippet": term.example_code_snippet,
        "real_world_example": term.real_world_example,
        "difficulty": term.difficulty,
    }
 
 
# ---------- GAME ----------
@app.post("/game/question", response_model=QuestionResponse)
def create_question(req: QuestionRequest, current_user: User = Depends(get_current_user), db=Depends(get_db)):
    all_terms = db.query(Term).all()
    if len(all_terms) < 2:
        raise HTTPException(status_code=400, detail="Not enough terms")
 
    try:
        cutoff = datetime.now() - timedelta(minutes=30)
        session_attempts = db.query(Attempt).filter(
            Attempt.user_id == current_user.id,
            Attempt.created_at > cutoff
        ).all()
        seen_ids = [a.term_id for a in session_attempts]
    except Exception:
        seen_ids = []  # if DB doesn't have created_at yet
 
    available_terms = [t for t in all_terms if t.id not in seen_ids]
    if len(available_terms) < 2:
        available_terms = all_terms
 
    correct_term = random.choice(available_terms)
 
    clue_type = req.mode if req.mode in ["definition", "code", "example"] else "definition"
    clue_text = correct_term.short_definition if clue_type == "definition" else (
        correct_term.example_code_snippet if clue_type == "code" else correct_term.real_world_example
    )
 
    hint_text = f"Difficulty: {correct_term.difficulty}, starts with '{correct_term.term[0].upper()}'"
 
    distractors = [t for t in all_terms if t.id != correct_term.id]
    random.shuffle(distractors)
    options_terms = [correct_term] + distractors[:3]
    random.shuffle(options_terms)
 
    options = [QuestionOption(term_id=t.id, term=t.term) for t in options_terms]
 
    return QuestionResponse(
        term_id=correct_term.id,
        clue_type=clue_type,
        clue_text=clue_text,
        options=options,
        hint=hint_text,
    )
 
 
@app.post("/game/answer", response_model=AnswerResponse)
def answer_question(
    req: AnswerRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    term = db.query(Term).filter(Term.id == req.term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
 
    correct = req.selected_term_id == req.term_id
    attempt = Attempt(user_id=current_user.id, term_id=term.id, is_correct=correct)
    db.add(attempt)
    db.commit()
 
    attempts = db.query(Attempt).filter(Attempt.user_id == current_user.id).all()
    points = sum(10 for a in attempts if a.is_correct)
 
    return AnswerResponse(
        correct=correct,
        message="Correct!" if correct else f"Incorrect. Correct answer: {term.term}",
        new_score=points,
        explanation=f"{term.term}: {term.detailed_explanation}",
    )
 
 
# ---------- STATS ----------
@app.get("/users/me/stats", response_model=StatsResponse)
def get_my_stats(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    attempts = db.query(Attempt).filter(Attempt.user_id == current_user.id).all()
    total = len(attempts)
    correct = len([a for a in attempts if a.is_correct])
 
    return StatsResponse(
        user_id=current_user.id,
        total_questions=total,
        correct_answers=correct,
        accuracy=round((correct / total * 100) if total else 0, 2),
        total_points=correct * 10,
    )
 
