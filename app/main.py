"""
Main FastAPI application for the Meeting Agent system.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.api import meetings
from app.websocket import handler as websocket_handler
from app.services.recall_service import RecallService
from app.services.deepgram_service import DeepgramService
from app.services.openai_service import OpenAIService
from app.services.redis_service import RedisService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Service instances
recall_service: RecallService = None
deepgram_service: DeepgramService = None
openai_service: OpenAIService = None
redis_service: RedisService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Meeting Agent application...")
    settings = get_settings()
    
    # Initialize services
    global recall_service, deepgram_service, openai_service, redis_service
    
    recall_service = RecallService(settings.recall_api_key)
    deepgram_service = DeepgramService(settings.deepgram_api_key)
    openai_service = OpenAIService(settings.openai_api_key)
    redis_service = RedisService(settings.redis_url)
    
    # Connect to Redis
    await redis_service.connect()
    
    # Initialize API routes with services
    meetings.init_services(recall_service, openai_service, redis_service)
    
    # Initialize WebSocket handler with services
    websocket_handler.init_services(deepgram_service, redis_service)
    
    logger.info("All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Meeting Agent application...")
    await redis_service.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Meeting Agent API",
    description="AI-powered meeting agent that joins meetings, provides briefings, and answers questions",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(meetings.router)


# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time audio/transcription streaming.
    
    Args:
        websocket: WebSocket connection
        user_id: User identifier
    """
    await websocket_handler.handle_websocket(websocket, user_id)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "Meeting Agent API",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        API information
    """
    return {
        "name": "Meeting Agent API",
        "version": "1.0.0",
        "description": "AI-powered meeting agent system",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True if settings.app_env == "development" else False,
        log_level=settings.log_level.lower()
    )
