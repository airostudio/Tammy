"""Main FastAPI application for Tammy AI Assistant"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.database import init_db, close_db
from app.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Tammy AI Assistant...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Tammy AI Assistant...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Tammy - AI Virtual Executive Assistant & Receptionist",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Tammy AI Assistant!",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "api": "/api",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": "2025-11-09",
    }


@app.get("/info")
async def info():
    """Application information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI Virtual Executive Assistant & Receptionist",
        "features": [
            "Calendar & Time Management",
            "Communication Management",
            "Task & Project Coordination",
            "Visitor & Call Management",
            "Contact & Relationship Management",
            "Natural Language Interface",
            "24/7 Availability",
            "Multi-channel Support",
        ],
        "api_docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
