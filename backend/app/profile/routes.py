"""
User Profile Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.auth.models import User
from app.profile.schemas import ProfileUpdate, PasswordChange, ProfileResponse
from app.profile.service import get_user_profile, update_user_profile, change_password

router = APIRouter()


@router.get("/profile/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile
    """
    profile = get_user_profile(db, current_user.id)
    
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        nickname=profile.nickname,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        phone=profile.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )


@router.put("/profile/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    """
    user = update_user_profile(db, current_user, profile_data)
    profile = get_user_profile(db, user.id)
    
    return ProfileResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        nickname=profile.nickname,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        phone=profile.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )


@router.put("/profile/password", status_code=status.HTTP_200_OK)
async def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    """
    change_password(db, current_user, password_data)
    return {"message": "Password changed successfully"}

