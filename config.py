"""
Core configuration module for GitHub Profile Analyzer
Handles all environment variables and application settings
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # GitHub Configuration
    github_token: str = ""
    
    # Gemini API Configuration
    gemini_api_key: str = ""
    
    # API Server Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_reload: bool = True
    
    # Database Configuration
    database_url: str = "sqlite:///./github_analyzer.db"
    
    # Environment
    environment: Literal["development", "production", "testing"] = "development"
    
    # Analysis Configuration
    max_repos_analyzed: int = 6
    commit_history_months: int = 12
    readme_min_length: int = 500
    
    class Config:
        """Pydantic config"""
        # Find .env in the root directory (parent of 'backend' folder)
        env_file = os.path.join(
            Path(__file__).parent.parent.parent,
            ".env"
        )
        case_sensitive = False


# Global settings instance
settings = Settings()

# Validate critical settings
if not settings.github_token:
    raise ValueError(
        "❌ GITHUB_TOKEN not found in environment variables!\n"
        f"   Expected .env file at: {Settings.Config.env_file}\n"
        "   Please ensure your .env file contains: GITHUB_TOKEN=your_token_here"
    )
