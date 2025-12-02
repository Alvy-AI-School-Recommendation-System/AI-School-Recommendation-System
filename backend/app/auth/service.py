"""
Authentication Service: Business Logic
"""
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import bcrypt
import hashlib
from app.auth.models import User
from app.auth.schemas import UserRegister, UserLogin
from app.common.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError
)

# Password encryption context
# Use bcrypt with appropriate rounds
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # If passlib fails, use direct bcrypt verification
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    # bcrypt limits password length to 72 bytes, hash first if exceeds
    password_bytes = password.encode('utf-8')
    password_to_hash = password
    
    # If password exceeds 72 bytes, hash with SHA256 first
    if len(password_bytes) > 72:
        password_to_hash = hashlib.sha256(password_bytes).hexdigest()
    
    try:
        return pwd_context.hash(password_to_hash)
    except Exception as e:
        # If passlib fails, use direct bcrypt
        print(f"Warning: passlib hashing failed, using direct bcrypt: {e}")
        password_bytes = password_to_hash.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')


def create_user(db: Session, user_data: UserRegister) -> User:
    """
    Create new user
    
    Args:
        db: Database session
        user_data: User registration data
    
    Returns:
        Created user object
    
    Raises:
        UserAlreadyExistsError: User already exists
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise UserAlreadyExistsError()
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise UserAlreadyExistsError()
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False  # Default unverified, can add email verification later
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, login_data: UserLogin) -> User:
    """
    Authenticate user login
    
    Args:
        db: Database session
        login_data: Login data
    
    Returns:
        User object
    
    Raises:
        InvalidCredentialsError: Invalid credentials
        UserNotFoundError: User not found
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise InvalidCredentialsError()
    
    if not user.hashed_password:
        raise InvalidCredentialsError()
    
    if not verify_password(login_data.password, user.hashed_password):
        raise InvalidCredentialsError()
    
    if not user.is_active:
        raise InvalidCredentialsError()
    
    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Get user by ID
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        User object
    
    Raises:
        UserNotFoundError: User not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError()
    return user


def get_user_by_email(db: Session, email: str) -> User:
    """
    Get user by email
    
    Args:
        db: Database session
        email: User email
    
    Returns:
        User object or None
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str) -> User:
    """
    Get user by Google ID
    
    Args:
        db: Database session
        google_id: Google user ID
    
    Returns:
        User object or None
    """
    return db.query(User).filter(User.google_id == google_id).first()

