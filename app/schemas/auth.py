from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: str
    role: str
    company_id: int
    store_id: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    username: str
    email: EmailStr
    role: str
    company_id: int
    store_id: Optional[int]
    is_super_admin: bool


class LoginResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str
    user: UserResponse
