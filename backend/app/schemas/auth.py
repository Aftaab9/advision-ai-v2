from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    organization_name: str  # Will create org if first user


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    org_id: Optional[UUID] = None
    role: Optional[str] = None
