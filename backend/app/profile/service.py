"""
User Profile Service: Business Logic
"""
from sqlalchemy.orm import Session
from app.auth.models import User
from app.profile.models import UserProfile
from app.profile.schemas import ProfileUpdate, PasswordChange
from app.auth.service import verify_password, get_password_hash
from app.common.exceptions import InvalidCredentialsError, UserAlreadyExistsError


def get_user_profile(db: Session, user_id: int) -> UserProfile:
    """
    Get user profile (create if not exists)
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        User profile object
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        # If not exists, create default profile
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


def update_user_profile(
    db: Session,
    user: User,
    profile_data: ProfileUpdate
) -> User:
    """
    Update user profile
    
    Args:
        db: Database session
        user: User object
        profile_data: Profile update data
    
    Returns:
        Updated user object
    """
    # Update user basic information
    if profile_data.username is not None and profile_data.username != user.username:
        # Check if username is already taken
        existing_user = db.query(User).filter(
            User.username == profile_data.username,
            User.id != user.id
        ).first()
        if existing_user:
            raise UserAlreadyExistsError()
        user.username = profile_data.username
    
    # Get or create user profile
    profile = get_user_profile(db, user.id)
    
    # Update profile information
    if profile_data.nickname is not None:
        profile.nickname = profile_data.nickname
    if profile_data.avatar_url is not None:
        profile.avatar_url = profile_data.avatar_url
    if profile_data.bio is not None:
        profile.bio = profile_data.bio
    if profile_data.phone is not None:
        profile.phone = profile_data.phone
    
    db.commit()
    db.refresh(user)
    db.refresh(profile)
    
    return user


def change_password(
    db: Session,
    user: User,
    password_data: PasswordChange
) -> User:
    """
    Change password
    
    Args:
        db: Database session
        user: User object
        password_data: Password data
    
    Returns:
        User object
    
    Raises:
        InvalidCredentialsError: Old password is incorrect
    """
    # Verify old password
    if not user.hashed_password:
        raise InvalidCredentialsError()
    
    if not verify_password(password_data.old_password, user.hashed_password):
        raise InvalidCredentialsError()
    
    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    db.refresh(user)
    
    return user

