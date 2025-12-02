"""
Custom Exception Classes
"""
from fastapi import HTTPException, status


class UserNotFoundError(HTTPException):
    """User not found exception"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class UserAlreadyExistsError(HTTPException):
    """User already exists exception"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )


class InvalidCredentialsError(HTTPException):
    """Invalid credentials exception"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


class InactiveUserError(HTTPException):
    """Inactive user exception"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been disabled"
        )

