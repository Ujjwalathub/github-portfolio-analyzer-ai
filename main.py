"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import router
from app.models.database import init_db
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting GitHub Profile Analyzer...")
    
    # Validate GitHub token is loaded
    if settings.github_token:
        token_preview = settings.github_token[:10] + "..." if len(settings.github_token) > 10 else "***"
        logger.info(f"✅ GitHub Token loaded successfully: {token_preview}")
    else:
        logger.error("❌ GitHub Token NOT loaded - check your .env file!")
        raise ValueError("GitHub token must be configured in .env file")
    
    if settings.gemini_api_key:
        logger.info("✅ Gemini API Key loaded successfully")
    else:
        logger.warning("⚠️ Gemini API Key not found - AI features may not work")
    
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down GitHub Profile Analyzer...")


# Create FastAPI app
app = FastAPI(
    title="GitHub Profile Analyzer",
    description="AI-driven GitHub profile analysis for recruiters",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GitHub Profile Analyzer API",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        timeout_keep_alive=300  # 5 minutes - increased to handle longer analyses
    )
