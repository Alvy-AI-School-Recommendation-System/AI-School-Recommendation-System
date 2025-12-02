"""
Application Configuration Management
Using pydantic-settings to manage environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional
import json


class Settings(BaseSettings):
    """Application configuration"""
    
    # Application basic configuration
    APP_NAME: str = "Login System API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/logindb"
    
    # JWT configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google OAuth configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # CORS configuration
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        json_schema_extra={
            "description": "List of allowed CORS origins, can be JSON string or comma-separated string"
        }
    )
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS, supports JSON string or list"""
        if isinstance(v, str):
            # Try to parse JSON string
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, try to split by comma
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # API prefix
    API_V1_PREFIX: str = "/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

