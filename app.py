"""
Streamlit frontend for GitHub Profile Analyzer
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="GitHub Profile Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .score-container {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .score-excellent {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .score-good {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .score-poor {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)


def get_score_color(score: float) -> str:
    """Determine color based on score"""
    if score >= 75:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"


def get_score_class(score: float) -> str:
    """Get CSS class based on score"""
    if score >= 75:
        return "score-excellent"
    elif score >= 50:
        return "score-good"
    else:
        return "score-poor"


def render_score_card(label: str, score: float, weight: float = None):
    """Render a score card"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(label, f"{score:.1f}/100", f"Weight: {weight*100:.0f}%" if weight else "")
    
    th = st.progress(score / 100)


def main():
    """Main Streamlit app"""
    
    # Sidebar
    with st.sidebar:
        st.title("🔍 GitHub Analyzer")
        
        st.markdown("---")
        
        # API configuration
        api_url = st.text_input(
            "Backend API URL",
            value="http://localhost:8000",
            help="URL of the FastAPI backend"
        )
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["Analyzer", "Leaderboard"],
            label_visibility="collapsed"
        )
    
    if page == "Analyzer":
        render_analyzer_page(api_url)
    elif page == "Leaderboard":
        render_leaderboard_page(api_url)


def render_analyzer_page(api_url: str):
    """Render the main analyzer page"""
    
    st.title("GitHub Profile Analyzer")
    st.markdown("Discover your coding potential through recruiter insights")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        username = st.text_input(
            "GitHub Username",
            placeholder="e.g., torvalds",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    if analyze_button:
        if not username:
            st.error("Please enter a GitHub username")
            return
        
        with st.spinner(f"Analyzing @{username}..."):
            try:
                response = requests.get(
                    f"{api_url}/api/analyze",
                    params={"username": username},
                    timeout=30
                )
                
                if response.status_code == 200:
                    analysis = response.json()
                    render_analysis_results(analysis)
                else:
                    error_data = response.json()
                    st.error(f"❌ {error_data.get('detail', 'Analysis failed')}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure the API is running.")
            except requests.exceptions.Timeout:
                st.error("❌ Request timeout. The analysis took too long.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def render_analysis_results(analysis: Dict[str, Any]):
    """Render analysis results"""
    
    # Profile header
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.image(analysis["avatar_url"], width=100)
    
    with col2:
        st.markdown(f"## {analysis.get('name', analysis['username'])}")
        st.markdown(f"**@{analysis['username']}** | {analysis.get('public_repos', 0)} repos | {analysis.get('followers', 0)} followers")
        if analysis.get("bio"):
            st.write(analysis["bio"])
    
    st.markdown("---")
    
    # Main score
    score_color = get_score_color(analysis["scores"]["total_score"])
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
        <h2 style="margin: 0;">Portfolio Score</h2>
        <h1 style="margin: 10px 0; font-size: 60px;">{analysis["scores"]["total_score"]:.1f}</h1>
        <p style="margin: 0;">Overall Hiring Potential</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Score breakdown
    st.markdown("### Score Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = analysis["scores"]["documentation_score"]
        render_score_card("📚 Documentation", score, 0.30)
    
    with col2:
        score = analysis["scores"]["technical_depth_score"]
        render_score_card("⚙️ Technical Depth", score, 0.40)
    
    with col3:
        score = analysis["scores"]["activity_score"]
        render_score_card("📊 Activity", score, 0.30)
    
    st.markdown("---")
    
    # AI Insights
    st.markdown("### 🤖 AI-Powered Insights")
    
    insights = analysis["ai_insights"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💡 Developer Profile")
        st.info(insights["developer_profile"])
        
        st.markdown("#### ✅ Strong Signals")
        for signal in insights["strong_signals"]:
            st.success(f"**{signal['signal']}**\n{signal['explanation']}")
    
    with col2:
        st.markdown("#### ⚠️ Red Flags")
        for flag in insights["red_flags"]:
            st.warning(f"**{flag['flag']}**\n{flag['explanation']}")
        
        st.markdown("#### 🎯 Improvement Actions")
        for action in insights["improvement_actions"]:
            impact_emoji = "🔴" if action["impact"] == "high" else "🟡" if action["impact"] == "medium" else "🟢"
            st.info(f"{impact_emoji} **{action['action']}** ({action['impact']})\n{action['explanation']}")
    
    st.markdown("---")
    
    # Repositories visualization
    st.markdown("### 📦 Top Repositories")
    
    repos_data = []
    for repo in analysis["repositories"]:
        repos_data.append({
            "Name": repo["name"],
            "Language": repo["language"] or "Unknown",
            "⭐": repo["stars"],
            "README Quality": "✅" if repo["readme_quality"] else "❌"
        })
    
    st.dataframe(
        pd.DataFrame(repos_data),
        use_container_width=True,
        hide_index=True
    )
    
    # Activity chart
    st.markdown("### 📈 Commit Activity")
    
    commit_activity = analysis["commit_activity"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Commits", commit_activity["total_commits"])
    with col2:
        st.metric("Active Months", f"{commit_activity['active_months']}/{commit_activity['analysis_period_months']}")
    with col3:
        st.metric("Consistency", f"{commit_activity['consistency_score']:.1f}%")
    
    st.markdown("---")
    
    # Overall assessment
    st.markdown("### Final Assessment")
    st.info(f"**{insights['overall_assessment']}**")


def render_leaderboard_page(api_url: str):
    """Render the leaderboard page"""
    
    st.title("🏆 Top Developers Leaderboard")
    st.markdown("The highest-ranked GitHub profiles analyzed by our system")
    
    try:
        response = requests.get(
            f"{api_url}/api/leaderboard",
            params={"limit": 20},
            timeout=10
        )
        
        if response.status_code == 200:
            leaderboard = response.json()
            
            if leaderboard:
                df = pd.DataFrame([
                    {
                        "Rank": item["rank"],
                        "Username": f'[@{item["username"]}]({item["profile_url"]})',
                        "Score": f'{item["score"]:.1f}',
                    }
                    for item in leaderboard
                ])
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No analyses stored yet. Start analyzing profiles!")
        else:
            st.error("Failed to fetch leaderboard")
            
    except Exception as e:
        st.error(f"Error fetching leaderboard: {str(e)}")


if __name__ == "__main__":
    main()
