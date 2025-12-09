from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserOut(UserBase):
    id: UUID
    organization_id: UUID
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
