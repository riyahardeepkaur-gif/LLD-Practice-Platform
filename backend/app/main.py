from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api.problems import router as problems_router
from app.api.attempts import router as attempts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite tables and seed 3 core LLD problems on startup
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Backend API for LLD Practice Platform MVP",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],  # Allow frontend development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(problems_router)
app.include_router(attempts_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "llm_configured": settings.has_llm_configured
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to LLD Practice Platform API",
        "docs": "/docs",
        "health": "/api/health"
    }
