"""
API routes for GitHub Profile Analyzer
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import Optional
import re

from app.layers.data_extraction import DataExtractionLayer
from app.layers.ai_scoring import ScoringEngine, AIInsightEngine
from app.models.database import ProfileAnalysis, get_db, init_db
from app.models.schemas import (
    AnalysisResponse, AnalysisStoredResponse, ErrorResponse,
    RepositoryInfo, CommitActivity, ScoresResponse,
    StrongSignal, RedFlag, ImprovementAction, AIInsights
)
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["analysis"])


def extract_username(input_str: str) -> str:
    """
    Extract GitHub username from either a full URL or just the username.
    
    Args:
        input_str: GitHub URL (e.g., 'https://github.com/username') or just username
        
    Returns:
        str: Clean GitHub username
        
    Raises:
        ValueError: If input cannot be parsed
    """
    if not input_str or not input_str.strip():
        raise ValueError("Username or URL cannot be empty")
    
    input_str = input_str.strip()
    
    # Try to match GitHub URLs
    url_patterns = [
        r'https?://(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/?(?:\?.*)?$',
        r'github\.com/([a-zA-Z0-9_-]+)/?(?:\?.*)?$',
        r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in url_patterns:
        match = re.match(pattern, input_str)
        if match:
            return match.group(1)
    
    # If no URL pattern matches, assume it's a username
    if re.match(r'^[a-zA-Z0-9_-]+$', input_str):
        return input_str
    
    raise ValueError(f"Invalid GitHub username or URL: {input_str}")


@router.get("/analyze", response_model=AnalysisResponse)
async def analyze_profile(username: str, db: Session = Depends(get_db)):
    """
    Analyze a GitHub profile and return insights
    
    Args:
        username: GitHub username or full GitHub URL (e.g., 'https://github.com/username')
        
    Returns:
        Complete analysis with scores and AI insights
    """
    try:
        # Extract clean username from URL or username string
        try:
            clean_username = extract_username(username)
        except ValueError as e:
            logger.warning(f"Invalid username/URL format: {username} - {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid GitHub username or URL: {str(e)}")
        
        logger.info(f"Processing analysis request for: {clean_username} (input: {username})")
        
        # Validate API keys
        if not settings.github_token or settings.github_token.strip() == "":
            logger.error("GitHub API token not configured")
            raise HTTPException(
                status_code=500, 
                detail="Server configuration error: GitHub API token not set. Contact administrator."
            )
        
        if not settings.gemini_api_key or settings.gemini_api_key.strip() == "":
            logger.warning("Gemini API key not configured - AI insights will be limited")
        
        # Initialize layers
        data_layer = DataExtractionLayer(
            settings.github_token,
            max_repos=settings.max_repos_analyzed,
            months_history=settings.commit_history_months
        )
        scoring_engine = ScoringEngine()
        ai_engine = AIInsightEngine(settings.gemini_api_key) if settings.gemini_api_key else None
        
        # Extract data
        logger.info(f"Extracting data for user: {clean_username}")
        profile_data = data_layer.get_profile_data(clean_username)
        
        # Calculate scores
        logger.info(f"Calculating scores for: {clean_username}")
        scores = scoring_engine.calculate_score(profile_data)
        
        # Generate AI insights
        if ai_engine:
            logger.info(f"Generating AI insights for: {clean_username}")
            ai_insights = ai_engine.generate_insights(profile_data, scores)
        else:
            logger.warning(f"Skipping AI insights for {clean_username} - API key not configured")
            ai_insights = {
                "developer_profile": "AI insights unavailable - API key not configured",
                "strong_signals": [],
                "red_flags": [],
                "improvement_actions": [],
                "overall_assessment": "Unable to generate AI assessment at this time"
            }
        
        # Format response
        response = format_analysis_response(profile_data, scores, ai_insights)
        
        # Store in database
        store_analysis(db, profile_data, scores, ai_insights)
        
        logger.info(f"Successfully completed analysis for: {clean_username}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing profile: {str(e)}"
        )


@router.get("/analysis/{username}", response_model=AnalysisStoredResponse)
async def get_stored_analysis(username: str, db: Session = Depends(get_db)):
    """
    Retrieve stored analysis for a user
    
    Args:
        username: GitHub username or full GitHub URL
        
    Returns:
        Stored analysis data
    """
    try:
        # Extract clean username
        clean_username = extract_username(username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid username: {str(e)}")
    
    analysis = db.query(ProfileAnalysis).filter(
        ProfileAnalysis.username == clean_username
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No analysis found for user: {clean_username}")
    
    return analysis


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get leaderboard of top analyzed profiles
    
    Args:
        limit: Number of top profiles to return
        
    Returns:
        List of top profiles by score
    """
    analyses = db.query(ProfileAnalysis).order_by(
        ProfileAnalysis.total_score.desc()
    ).limit(limit).all()
    
    return [
        {
            "rank": idx + 1,
            "username": a.username,
            "score": a.total_score,
            "profile_url": a.profile_url
        }
        for idx, a in enumerate(analyses)
    ]


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


def format_analysis_response(
    profile_data: dict,
    scores: dict,
    ai_insights: dict
) -> AnalysisResponse:
    """Format raw data into response model"""
    
    # Convert repositories
    repositories = [
        RepositoryInfo(
            name=repo["name"],
            url=repo["url"],
            language=repo.get("language"),
            stars=repo.get("stars", 0),
            description=repo.get("description"),
            readme_quality=repo.get("readme_quality", False),
            readme_length=repo.get("readme_length", 0)
        )
        for repo in profile_data.get("repositories", [])
    ]
    
    # Format scores
    scores_response = ScoresResponse(
        total_score=scores["total_score"],
        documentation_score=scores["documentation_score"],
        technical_depth_score=scores["technical_depth_score"],
        activity_score=scores["activity_score"]
    )
    
    # Format commit activity
    commit_activity = CommitActivity(
        **profile_data.get("commit_activity", {})
    )
    
    # Format AI insights
    ai_insights_response = AIInsights(
        developer_profile=ai_insights.get("developer_profile", ""),
        strong_signals=[
            StrongSignal(**signal) for signal in ai_insights.get("strong_signals", [])
        ],
        red_flags=[
            RedFlag(**flag) for flag in ai_insights.get("red_flags", [])
        ],
        improvement_actions=[
            ImprovementAction(**action) for action in ai_insights.get("improvement_actions", [])
        ],
        overall_assessment=ai_insights.get("overall_assessment", "")
    )
    
    return AnalysisResponse(
        username=profile_data["username"],
        name=profile_data.get("name"),
        bio=profile_data.get("bio"),
        profile_url=profile_data["profile_url"],
        avatar_url=profile_data["avatar_url"],
        public_repos=profile_data["public_repos"],
        followers=profile_data["followers"],
        scores=scores_response,
        repositories=repositories,
        commit_activity=commit_activity,
        ai_insights=ai_insights_response,
        analyzed_at=datetime.utcnow()
    )


def store_analysis(
    db: Session,
    profile_data: dict,
    scores: dict,
    ai_insights: dict
) -> None:
    """Store analysis results in database"""
    try:
        # Check if analysis already exists
        existing = db.query(ProfileAnalysis).filter(
            ProfileAnalysis.username == profile_data["username"]
        ).first()
        
        if existing:
            # Update existing
            existing.total_score = scores["total_score"]
            existing.documentation_score = scores["documentation_score"]
            existing.technical_depth_score = scores["technical_depth_score"]
            existing.activity_score = scores["activity_score"]
            existing.profile_data = profile_data
            existing.ai_insights = ai_insights
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            analysis = ProfileAnalysis(
                username=profile_data["username"],
                name=profile_data.get("name"),
                bio=profile_data.get("bio"),
                profile_url=profile_data["profile_url"],
                avatar_url=profile_data["avatar_url"],
                total_score=scores["total_score"],
                documentation_score=scores["documentation_score"],
                technical_depth_score=scores["technical_depth_score"],
                activity_score=scores["activity_score"],
                public_repos=profile_data["public_repos"],
                followers=profile_data["followers"],
                following=profile_data.get("following", 0),
                profile_data=profile_data,
                ai_insights=ai_insights
            )
            db.add(analysis)
        
        db.commit()
    except Exception as e:
        logger.error(f"Error storing analysis: {str(e)}")
        db.rollback()
