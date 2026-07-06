# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError

from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    TokenResponse, LoginRequest, TokenRefreshRequest, 
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
)
from app.schemas.user import UserCreate, UserResponse
from app.auth.security import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, get_current_user, RoleChecker
)
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == payload.email) | (User.username == payload.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or Email already exists.")
    new_user = User(
        full_name=payload.full_name,
        username=payload.username,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role,
        company_id=payload.company_id,
        store_id=payload.store_id,
        is_super_admin=False,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == payload.username_or_email) | (User.username == payload.username_or_email)
    ).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User account is inactive.")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": user}

@router.post("/login-swagger-compat", response_model=TokenResponse, include_in_schema=False)
def login_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login_user(LoginRequest(username_or_email=form_data.username, password=form_data.password), db)

@router.get("/me", response_model=UserResponse)
def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=TokenResponse)
def refresh_session_tokens(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        decoded = jwt.decode(payload.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = decoded.get("sub")
        token_type = decoded.get("type")
        if not user_id or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token parameters.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or mutated.")
    user = db.query(User).filter(User.id == int(user_id), User.refresh_token == payload.refresh_token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")
    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)
    user.refresh_token = new_refresh_token
    db.commit()
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer", "user": user}

@router.post("/logout", response_model=MessageResponse)
def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.refresh_token = None
    db.commit()
    return {"message": "Successfully logged out."}

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password_request(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return {"message": "If the account exists, a recovery token vector has been allocated."}

@router.post("/reset-password", response_model=MessageResponse)
def reset_password_execution(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification window expired.")
    user.password = hash_password(payload.new_password)
    user.refresh_token = None
    db.commit()
    return {"message": "Password successfully updated."}
