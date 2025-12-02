"""
Google OAuth Handler
"""
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session
from app.config import settings
from app.auth.models import User
from app.auth.service import get_user_by_email, get_user_by_google_id, create_user
from app.common.exceptions import UserAlreadyExistsError


async def verify_google_token(token: str) -> dict:
    """
    Verify Google ID token
    
    Args:
        token: Google ID token
    
    Returns:
        Decoded token information (contains email, name, sub, etc.)
    
    Raises:
        ValueError: token is invalid
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not settings.GOOGLE_CLIENT_ID:
        raise ValueError("GOOGLE_CLIENT_ID is not configured")
    
    try:
        # Verify token
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Verify issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError(f'Wrong issuer: {idinfo.get("iss")}. Expected accounts.google.com')
        
        # Verify audience (Client ID)
        if idinfo.get('aud') != settings.GOOGLE_CLIENT_ID:
            raise ValueError(
                f'Token audience mismatch. Token was issued for: {idinfo.get("aud")}, '
                f'but expected: {settings.GOOGLE_CLIENT_ID}'
            )
        
        return idinfo
    except ValueError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise ValueError(f"Invalid Google token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise ValueError(f"Token verification error: {str(e)}")


async def get_or_create_user_from_google(
    db: Session,
    google_user_info: dict
) -> User:
    """
    Get or create user from Google user information
    
    Args:
        db: Database session
        google_user_info: Google user information (returned from verify_google_token)
    
    Returns:
        User object
    """
    google_id = google_user_info.get('sub')
    email = google_user_info.get('email')
    name = google_user_info.get('name', '')
    
    if not google_id or not email:
        raise ValueError("Missing required Google user information")
    
    # First try to find by Google ID
    user = get_user_by_google_id(db, google_id)
    if user:
        return user
    
    # Then try to find by email (might be an existing user)
    user = get_user_by_email(db, email)
    if user:
        # If user exists but doesn't have Google ID, associate Google ID
        if not user.google_id:
            user.google_id = google_id
            db.commit()
            db.refresh(user)
        return user
    
    # Create new user
    # Generate username (use email prefix if name not provided)
    username = name.replace(' ', '_').lower() if name else email.split('@')[0]
    # Ensure username is unique
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{counter}"
        counter += 1
    
    new_user = User(
        email=email,
        username=username,
        hashed_password=None,  # Google login users don't have passwords
        google_id=google_id,
        is_active=True,
        is_verified=True  # Google has verified the email
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

