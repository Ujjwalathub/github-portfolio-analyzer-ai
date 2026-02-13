"""
Pydantic response models for API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RepositoryInfo(BaseModel):
    """Repository information"""
    name: str
    url: str
    language: Optional[str]
    stars: int
    description: Optional[str]
    readme_quality: bool
    readme_length: int


class CommitActivity(BaseModel):
    """Commit activity metrics"""
    total_commits: int
    active_months: int
    consistency_score: float
    analysis_period_months: int


class ScoresResponse(BaseModel):
    """Score breakdown"""
    total_score: float
    documentation_score: float
    technical_depth_score: float
    activity_score: float


class StrongSignal(BaseModel):
    """AI-detected strong signal"""
    signal: str
    explanation: str


class RedFlag(BaseModel):
    """AI-detected red flag"""
    flag: str
    explanation: str


class ImprovementAction(BaseModel):
    """Suggested improvement action"""
    action: str
    impact: str  # high, medium, low
    explanation: str


class AIInsights(BaseModel):
    """AI-generated insights"""
    developer_profile: str
    strong_signals: List[StrongSignal]
    red_flags: List[RedFlag]
    improvement_actions: List[ImprovementAction]
    overall_assessment: str


class AnalysisResponse(BaseModel):
    """Complete analysis response"""
    username: str
    name: Optional[str]
    bio: Optional[str]
    profile_url: str
    avatar_url: str
    
    public_repos: int
    followers: int
    
    scores: ScoresResponse
    repositories: List[RepositoryInfo]
    commit_activity: CommitActivity
    ai_insights: AIInsights
    
    analyzed_at: datetime


class AnalysisStoredResponse(BaseModel):
    """Response when analysis is stored in database"""
    id: int
    username: str
    total_score: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    details: Optional[str] = None
