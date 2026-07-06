# app/main.py
from fastapi import FastAPI
from app.core.database import engine
from app.models.base import Base
from app.routes.auth import router as auth_router

app = FastAPI(
    title="SetuPOS Enterprise API",
    version="1.0.0",
    description="Production-ready backend engine for SetuPOS Enterprise",
)

# Initialize database tables if they do not exist
Base.metadata.create_all(bind=engine)

# Register routers with global API prefix
app.include_router(auth_router, prefix="/api/v1")

@app.get("/", tags=["Infrastructure"])
def home():
    return {
        "status": "running",
        "project": "SetuPOS Enterprise",
        "engine": "FastAPI Node"
    }

@app.get("/auth/health", tags=["Infrastructure"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

































