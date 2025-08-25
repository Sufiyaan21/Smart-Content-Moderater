from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import structlog

from app.core.config import settings
from app.core.logger import get_logger, setup_logging
from app.db.base import init_db
from app.routes import moderation, analytics
from app.schemas.schemas import HealthCheckResponse, ErrorResponse

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Smart Content Moderator API")
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Content Moderator API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A smart content moderation API using Google Gemini for text and image analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error("Unhandled exception", 
                path=request.url.path,
                method=request.method,
                error=str(exc),
                exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error="Internal Server Error",
            message="An unexpected error occurred",
            details={"path": str(request.url.path)}
        ).dict()
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Smart Content Moderator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "text_moderation": "/api/v1/moderate/text",
            "image_moderation": "/api/v1/moderate/image",
            "user_analytics": "/api/v1/analytics/summary",
            "all_analytics": "/api/v1/analytics/summary/all"
        }
    }


# Include routers
app.include_router(moderation.router)
app.include_router(analytics.router)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = datetime.now()
    
    # Log request
    logger.info("Incoming request",
                method=request.method,
                path=request.url.path,
                client_ip=request.client.host if request.client else None)
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info("Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time=f"{process_time:.3f}s")
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )



