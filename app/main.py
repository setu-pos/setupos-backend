from fastapi import FastAPI

from app.core.database import engine
from app.models.base import Base
from app.models.user import User
from app.routes.auth import router as auth_router

app = FastAPI(
    title="SetuPOS Backend",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "status": "running",
        "app": "SetuPOS Backend",
        "message": "Welcome to SetuPOS Cloud API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
