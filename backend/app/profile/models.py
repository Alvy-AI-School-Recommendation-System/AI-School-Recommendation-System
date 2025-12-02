"""
User Profile Model
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserProfile(Base):
    """User profile model"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    avatar_url = Column(String, nullable=True)  # Avatar URL
    nickname = Column(String, nullable=True)  # Nickname
    bio = Column(Text, nullable=True)  # Biography
    phone = Column(String, nullable=True)  # Phone number
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User relationship
    user = relationship("User", backref="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, nickname={self.nickname})>"

