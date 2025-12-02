"""
User Profile-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class ProfileUpdate(BaseModel):
    """Update profile request"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    nickname: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)


class PasswordChange(BaseModel):
    """Change password request"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class ProfileResponse(BaseModel):
    """Profile response"""
    id: int
    email: str
    username: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

