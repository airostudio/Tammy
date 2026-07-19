"""Main FastAPI application for Tammy AI Assistant"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import os

from app.config import get_settings
from app.database import init_db, close_db
from app.api import api_router

settings = get_settings()

# Configure logging
log_handlers = [logging.StreamHandler()]
if settings.log_file:
    try:
        log_dir = os.path.dirname(settings.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        log_handlers.append(logging.FileHandler(settings.log_file))
    except OSError:
        # Read-only filesystem (e.g. serverless deployments) - fall back to stream logging only
        pass

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=log_handlers,
)
logger = logging.getLogger(__name__)


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

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Serve the web interface"""
    index_path = os.path.join(public_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # Fallback to JSON response
        return {
            "message": "Welcome to Tammy AI Assistant!",
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
            "api": "/api",
            "web_interface": "Install frontend files to see the web interface"
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
