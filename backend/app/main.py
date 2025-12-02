"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.auth.routes import router as auth_router
from app.profile.routes import router as profile_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure CORS
# Print CORS configuration for debugging
print(f"CORS Configuration - Allowed Origins: {settings.CORS_ORIGINS}")

# Print Google OAuth configuration status
if settings.GOOGLE_CLIENT_ID:
    print(f"✓ Google OAuth configured - Client ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
else:
    print("⚠ Google OAuth not configured - Please set GOOGLE_CLIENT_ID in backend/.env")

# Add request logging middleware for CORS debugging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

class CORSDebugMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        method = request.method
        path = request.url.path
        logger.info(f"CORS Debug - Method: {method}, Path: {path}, Origin: {origin}")
        response = await call_next(request)
        cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
        logger.info(f"CORS Response Headers: {cors_headers}")
        return response

app.add_middleware(CORSDebugMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register routes
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(profile_router, prefix=settings.API_V1_PREFIX, tags=["User Profile"])


@app.get("/")
async def root():
    """Root path"""
    return {
        "message": "Login System API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}


@app.get("/debug/cors")
async def debug_cors():
    """Debug CORS configuration"""
    return {
        "cors_origins": settings.CORS_ORIGINS,
        "cors_origins_type": str(type(settings.CORS_ORIGINS)),
        "cors_origins_length": len(settings.CORS_ORIGINS) if isinstance(settings.CORS_ORIGINS, list) else "not a list"
    }
