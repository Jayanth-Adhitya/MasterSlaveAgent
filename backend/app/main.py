"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.services.redis_service import close_redis
from app.routers import auth, messages, notifications, websocket

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logging.info("Starting application...")
    yield
    # Shutdown
    logging.info("Shutting down application...")
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Multi-tenant conversational assistant PoC",
    lifespan=lifespan,
)

# CORS middleware for frontend
# Allow all origins for WebSocket connections through proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(websocket.router)


@app.get("/health")
async def health_check_root():
    """Root health check endpoint for Docker."""
    return {"status": "healthy"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.app_name}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "health": "/api/health",
    }
