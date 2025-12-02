"""
JWT Token Generation and Verification
"""
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create access token
    
    Args:
        data: Data to encode (usually contains user ID)
        expires_delta: Expiration time delta
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Convert datetime to Unix timestamp (integer) for JWT exp claim
    to_encode.update({"exp": int(expire.timestamp()), "type": "access"})
    # Ensure sub is a string (JWT standard requirement)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create refresh token
    
    Args:
        data: Data to encode
    
    Returns:
        JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Convert datetime to Unix timestamp (integer) for JWT exp claim
    to_encode.update({"exp": int(expire.timestamp()), "type": "refresh"})
    # Ensure sub is a string (JWT standard requirement)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload
    
    Raises:
        JWTError: token is invalid or expired
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    return payload

