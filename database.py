"""
Database models for GitHub Profile Analyzer
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import settings

Base = declarative_base()


class ProfileAnalysis(Base):
    """Stores analyzed GitHub profile data"""
    
    __tablename__ = "profile_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    profile_url = Column(String)
    avatar_url = Column(String)
    
    # Scores
    total_score = Column(Float)
    documentation_score = Column(Float)
    technical_depth_score = Column(Float)
    activity_score = Column(Float)
    
    # Profile metrics
    public_repos = Column(Integer)
    followers = Column(Integer)
    following = Column(Integer)
    
    # Raw data (stored as JSON)
    profile_data = Column(JSON)
    ai_insights = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProfileAnalysis(username={self.username}, score={self.total_score})>"


class AnalysisCache(Base):
    """Caches raw GitHub data to avoid repeated API calls"""
    
    __tablename__ = "analysis_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    raw_profile_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_valid = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<AnalysisCache(username={self.username})>"


# Database setup
def get_database_engine():
    """Create and return database engine"""
    return create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )


def get_session_factory():
    """Create and return session factory"""
    engine = get_database_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    engine = get_database_engine()
    Base.metadata.create_all(bind=engine)


# Dependency for API routes
def get_db():
    """Get database session"""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
