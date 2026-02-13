"""
AI & Scoring Engine - The "Recruiter Brain"
Transforms raw data into objective scores and qualitative feedback
"""

import logging
from typing import Dict, List, Any
import json
import google.generativeai as genai

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Calculates deterministic scores based on weighted metrics"""
    
    # Weights for different scoring components
    WEIGHTS = {
        "documentation": 0.30,
        "technical_depth": 0.40,
        "activity": 0.30
    }
    
    def calculate_score(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate portfolio score using weighted metrics
        
        Args:
            profile_data: Extracted profile data from data layer
            
        Returns:
            Dictionary with score breakdown and metrics
        """
        doc_score = self._score_documentation(profile_data)
        tech_score = self._score_technical_depth(profile_data)
        activity_score = self._score_activity(profile_data)
        
        total_score = (
            doc_score * self.WEIGHTS["documentation"] +
            tech_score * self.WEIGHTS["technical_depth"] +
            activity_score * self.WEIGHTS["activity"]
        )
        
        return {
            "total_score": round(total_score, 2),
            "documentation_score": round(doc_score, 2),
            "technical_depth_score": round(tech_score, 2),
            "activity_score": round(activity_score, 2),
            "score_breakdown": {
                "documentation": {
                    "score": round(doc_score, 2),
                    "weight": self.WEIGHTS["documentation"]
                },
                "technical_depth": {
                    "score": round(tech_score, 2),
                    "weight": self.WEIGHTS["technical_depth"]
                },
                "activity": {
                    "score": round(activity_score, 2),
                    "weight": self.WEIGHTS["activity"]
                }
            }
        }
    
    def _score_documentation(self, profile_data: Dict[str, Any]) -> float:
        """
        Score based on documentation quality
        Evaluates README comprehensiveness and project storytelling
        
        Scale: 0-100
        """
        score = 0
        count = 0
        
        for repo in profile_data.get("repositories", []):
            readme_length = repo.get("readme_length", 0)
            has_description = bool(repo.get("description"))
            
            # Points for README
            if readme_length > 1000:
                count_score = 100
            elif readme_length > 500:
                count_score = 75
            elif readme_length > 100:
                count_score = 50
            else:
                count_score = 25
            
            # Bonus for having repo description
            if has_description:
                count_score += 10
            
            score += min(100, count_score)
            count += 1
        
        return (score / count) if count > 0 else 0
    
    def _score_technical_depth(self, profile_data: Dict[str, Any]) -> float:
        """
        Score based on technical complexity and diversity
        Evaluates language diversity and project complexity
        
        Scale: 0-100
        """
        repos = profile_data.get("repositories", [])
        
        # Language diversity
        languages = set()
        for repo in repos:
            if repo.get("language"):
                languages.add(repo["language"])
        
        language_score = min(100, len(languages) * 20)  # Max 100 at 5 languages
        
        # Project complexity (based on stars and forks)
        complexity_score = 0
        for repo in repos:
            stars = repo.get("stars", 0)
            forks = repo.get("forks", 0)
            
            if stars > 1000:
                complexity_score += 30
            elif stars > 100:
                complexity_score += 20
            elif stars > 10:
                complexity_score += 10
            else:
                complexity_score += 5
            
            if forks > 100:
                complexity_score += 20
            elif forks > 10:
                complexity_score += 10
        
        complexity_score = min(100, complexity_score // max(1, len(repos)))
        
        # Weighted average
        return (language_score * 0.4 + complexity_score * 0.6)
    
    def _score_activity(self, profile_data: Dict[str, Any]) -> float:
        """
        Score based on activity and consistency
        Rewards consistent commit frequency
        
        Scale: 0-100
        """
        commit_activity = profile_data.get("commit_activity", {})
        
        consistency = commit_activity.get("consistency_score", 0)
        total_commits = commit_activity.get("total_commits", 0)
        
        # Commit frequency bonus
        if total_commits > 1000:
            commit_bonus = 40
        elif total_commits > 500:
            commit_bonus = 30
        elif total_commits > 100:
            commit_bonus = 20
        else:
            commit_bonus = 10
        
        # Consistency is weighted more heavily
        activity_score = (consistency * 0.7) + (commit_bonus)
        
        return min(100, activity_score)


class AIInsightEngine:
    """Generates qualitative AI-driven insights using Gemini"""
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the AI engine
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-pro")
    
    def generate_insights(self, profile_data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate recruiter-focused insights using Gemini
        
        Args:
            profile_data: Extracted profile data
            scores: Calculated scores
            
        Returns:
            Dictionary with AI-generated insights
        """
        try:
            # Prepare summary for the prompt
            summary = self._prepare_summary(profile_data, scores)
            
            prompt = self._build_recruiter_prompt(summary)
            
            response = self.model.generate_content(prompt)
            
            insights = self._parse_insights(response.text)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return self._default_insights()
    
    def _prepare_summary(self, profile_data: Dict[str, Any], scores: Dict[str, Any]) -> str:
        """Prepare data summary for prompt"""
        summary = {
            "username": profile_data.get("username"),
            "name": profile_data.get("name"),
            "bio": profile_data.get("bio"),
            "followers": profile_data.get("followers"),
            "public_repos": profile_data.get("public_repos"),
            "total_score": scores.get("total_score"),
            "repositories": [
                {
                    "name": r.get("name"),
                    "language": r.get("language"),
                    "stars": r.get("stars"),
                    "description": r.get("description"),
                    "readme_quality": r.get("readme_quality")
                }
                for r in profile_data.get("repositories", [])[:5]
            ],
            "commit_activity": profile_data.get("commit_activity", {}).get("total_commits", 0),
            "languages": list(set([
                r.get("language") for r in profile_data.get("repositories", []) if r.get("language")
            ]))
        }
        return json.dumps(summary, indent=2)
    
    def _build_recruiter_prompt(self, summary: str) -> str:
        """Build the recruitment-focused prompt"""
        return f"""Act as a Technical Recruiter at a Top Tier Tech Firm.

Analyze the following GitHub profile data:

{summary}

Provide your analysis in the following JSON format:
{{
    "developer_profile": "Brief categorization (e.g., 'Full-Stack Engineer', 'Data Scientist')",
    "strong_signals": [
        {{"signal": "signal1", "explanation": "why this is positive"}},
        {{"signal": "signal2", "explanation": "why this is positive"}},
        {{"signal": "signal3", "explanation": "why this is positive"}}
    ],
    "red_flags": [
        {{"flag": "flag1", "explanation": "why this is concerning"}},
        {{"flag": "flag2", "explanation": "why this is concerning"}},
        {{"flag": "flag3", "explanation": "why this is concerning"}}
    ],
    "improvement_actions": [
        {{"action": "action1", "impact": "high/medium/low", "explanation": "why important"}},
        {{"action": "action2", "impact": "high/medium/low", "explanation": "why important"}},
        {{"action": "action3", "impact": "high/medium/low", "explanation": "why important"}}
    ],
    "overall_assessment": "2-3 sentence assessment of hiring potential"
}}

Return ONLY valid JSON, no additional text."""
    
    def _parse_insights(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini"""
        try:
            # Extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return self._default_insights()
    
    def _default_insights(self) -> Dict[str, Any]:
        """Return default insights when AI fails"""
        return {
            "developer_profile": "Unable to generate",
            "strong_signals": [{"signal": "Data unavailable", "explanation": ""}],
            "red_flags": [{"flag": "Analysis error", "explanation": ""}],
            "improvement_actions": [{"action": "Retry analysis", "impact": "high", "explanation": ""}],
            "overall_assessment": "Please try again later."
        }
