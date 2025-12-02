"""
Authentication Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.dependencies import get_current_user
from app.config import settings
from app.auth.models import User
from app.auth.schemas import (
    UserRegister,
    UserLogin,
    GoogleLoginRequest,
    Token,
    TokenRefresh,
    UserResponse
)
from app.auth.service import create_user, authenticate_user
from app.auth.jwt import create_access_token, create_refresh_token, verify_token
from app.auth.oauth import verify_google_token, get_or_create_user_from_google

router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    User registration
    """
    user = create_user(db, user_data)
    return user


@router.post("/auth/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login
    """
    user = authenticate_user(db, login_data)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/auth/config")
async def get_auth_config():
    """
    Get authentication configuration information (for frontend to determine if features are available)
    """
    return {
        "google_oauth_enabled": bool(settings.GOOGLE_CLIENT_ID),
        "google_client_id": settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None,
        "google_client_id_configured": bool(settings.GOOGLE_CLIENT_ID),
        "google_client_id_preview": (
            settings.GOOGLE_CLIENT_ID[:20] + "..." if settings.GOOGLE_CLIENT_ID and len(settings.GOOGLE_CLIENT_ID) > 20 
            else settings.GOOGLE_CLIENT_ID
        ) if settings.GOOGLE_CLIENT_ID else None
    }


@router.post("/auth/google/test")
async def test_google_token(
    google_data: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Test Google Token verification (for debugging only, does not create user)
    Returns token information but does not perform login
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Check configuration
    if not settings.GOOGLE_CLIENT_ID:
        return {
            "error": "Google OAuth not configured",
            "message": "GOOGLE_CLIENT_ID is not set in environment variables",
            "config_status": "missing"
        }
    
    try:
        logger.info(f"Testing Google token verification with Client ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
        
        # Verify Google token
        google_user_info = await verify_google_token(google_data.id_token)
        
        logger.info(f"Token verified successfully. User info: {google_user_info.get('email')}")
        
        return {
            "status": "success",
            "message": "Google token is valid",
            "user_info": {
                "email": google_user_info.get("email"),
                "name": google_user_info.get("name"),
                "sub": google_user_info.get("sub"),
                "email_verified": google_user_info.get("email_verified"),
                "picture": google_user_info.get("picture"),
            },
            "config_status": "valid",
            "client_id_used": settings.GOOGLE_CLIENT_ID[:20] + "..." if len(settings.GOOGLE_CLIENT_ID) > 20 else settings.GOOGLE_CLIENT_ID
        }
    except ValueError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "config_status": "invalid_token",
            "client_id_used": settings.GOOGLE_CLIENT_ID[:20] + "..." if len(settings.GOOGLE_CLIENT_ID) > 20 else settings.GOOGLE_CLIENT_ID
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "config_status": "error"
        }


@router.post("/auth/google", response_model=Token)
async def google_login(
    google_data: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Google login
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if Google OAuth is configured
    if not settings.GOOGLE_CLIENT_ID:
        logger.error("Google OAuth not configured: GOOGLE_CLIENT_ID is missing")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID in environment variables."
        )
    
    try:
        logger.info("Starting Google login process")
        
        # Verify Google token
        google_user_info = await verify_google_token(google_data.id_token)
        logger.info(f"Token verified for user: {google_user_info.get('email')}")
        
        # Get or create user
        user = await get_or_create_user_from_google(db, google_user_info)
        logger.info(f"User processed: {user.email} (ID: {user.id})")
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        logger.info(f"Login successful for user: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        logger.error(f"Google login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during Google login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token
    """
    try:
        payload = verify_token(token_data.refresh_token)
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Convert to integer
        user_id = int(user_id)
        
        # Verify user exists and is active
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return current_user

