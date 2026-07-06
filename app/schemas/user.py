from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.EMPLOYEE
    company_id: Optional[int] = None
    store_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    username: str
    email: EmailStr
    role: UserRole
    company_id: Optional[int]
    store_id: Optional[int]
    is_super_admin: bool
    is_active: bool

    class Config:
        from_attributes = True
