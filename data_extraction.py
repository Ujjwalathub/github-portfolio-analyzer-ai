"""
Data Extraction Layer - The "Signal" Collector
Responsible for gathering raw data from GitHub API
"""

from typing import Optional, Dict, List, Any
from github import Github, GithubException
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataExtractionLayer:
    """Extracts and structures GitHub profile data"""
    
    def __init__(self, github_token: str, max_repos: int = 6, months_history: int = 12):
        """
        Initialize the data extraction layer
        
        Args:
            github_token: GitHub API token
            max_repos: Maximum number of repositories to analyze
            months_history: Number of months to analyze for commit history
        """
        self.github = Github(github_token)
        self.max_repos = max_repos
        self.months_history = months_history
    
    def get_profile_data(self, username: str) -> Dict[str, Any]:
        """
        Extract complete profile data for a GitHub user
        
        Args:
            username: GitHub username
            
        Returns:
            Dictionary containing profile data
        """
        try:
            user = self.github.get_user(username)
            
            data = {
                "username": username,
                "name": user.name,
                "bio": user.bio,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "location": user.location,
                "email": user.email,
                "company": user.company,
                "blog": user.blog,
                "twitter": getattr(user, 'twitter_username', None) or getattr(user, 'twitter_login', None),
                "profile_url": user.html_url,
                "avatar_url": user.avatar_url,
                "repositories": self._extract_repository_data(user),
                "commit_activity": self._analyze_commit_history(user)
            }
            
            return data
            
        except GithubException as e:
            logger.error(f"GitHub API error for user {username}: {str(e)}")
            raise ValueError(f"Unable to fetch profile for {username}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching profile {username}: {str(e)}")
            raise
    
    def _extract_repository_data(self, user) -> List[Dict[str, Any]]:
        """
        Extract data from user's top repositories
        
        Args:
            user: GitHub user object
            
        Returns:
            List of repository data
        """
        repos_data = []
        
        try:
            # Get starred repos (quality indicator) plus others
            all_repos = sorted(
                user.get_repos(sort="stars", direction="desc"),
                key=lambda r: r.stargazers_count,
                reverse=True
            )
            
            for repo in all_repos[:self.max_repos]:
                repo_info = {
                    "name": repo.name,
                    "url": repo.html_url,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "watchers": repo.watchers_count,
                    "topics": repo.topics,
                    "is_fork": repo.fork,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                }
                
                # Extract README
                readme_content = self._extract_readme(repo)
                repo_info["readme_quality"] = len(readme_content) > 500
                repo_info["readme_length"] = len(readme_content)
                repo_info["readme_sample"] = readme_content[:1000]
                
                repos_data.append(repo_info)
                
        except Exception as e:
            logger.warning(f"Error extracting repository data: {str(e)}")
        
        return repos_data
    
    def _extract_readme(self, repo) -> str:
        """
        Extract README content from a repository
        
        Args:
            repo: GitHub repository object
            
        Returns:
            README content or empty string
        """
        try:
            readme = repo.get_contents("README.md")
            return readme.decoded_content.decode("utf-8")
        except:
            return ""
    
    def _analyze_commit_history(self, user) -> Dict[str, Any]:
        """
        Analyze commit history for activity tracking
        
        Args:
            user: GitHub user object
            
        Returns:
            Dictionary with commit activity metrics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.months_history * 30)
            total_commits = 0
            commits_by_month = {}
            
            for repo in user.get_repos():
                try:
                    commits = repo.get_commits(since=cutoff_date, author=user.login)
                    for commit in commits:
                        total_commits += 1
                        month_key = commit.commit.author.date.strftime("%Y-%m")
                        commits_by_month[month_key] = commits_by_month.get(month_key, 0) + 1
                except:
                    continue
            
            # Calculate consistency metric
            active_months = len(commits_by_month)
            expected_months = self.months_history
            consistency_score = (active_months / expected_months * 100) if expected_months > 0 else 0
            
            return {
                "total_commits": total_commits,
                "active_months": active_months,
                "consistency_score": min(100, consistency_score),  # 0-100
                "commits_by_month": commits_by_month,
                "analysis_period_months": self.months_history
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing commit history: {str(e)}")
            return {
                "total_commits": 0,
                "active_months": 0,
                "consistency_score": 0,
                "commits_by_month": {},
                "analysis_period_months": self.months_history
            }
