from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Authentication API Working"
    }

@router.post("/login")
def login():
    return {
        "success": True,
        "message": "Login API Ready"
    }

@router.post("/register")
def register():
    return {
        "success": True,
        "message": "Register API Ready"
    }
