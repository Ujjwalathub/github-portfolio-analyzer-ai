# GitHub Profile Analyzer

An AI-driven GitHub profile analysis system for recruiters. Leverages the "Request-Analyze-Visualize" pipeline to provide actionable insights from GitHub profiles in **under 2 minutes**.

## 🎯 Key Features

### Three-Layer Architecture

#### 1. **Data Extraction Layer** (The "Signal" Collector)
- Fetches comprehensive GitHub profile data using PyGithub
- Extracts repository information, READMEs, and commit history
- Analyzes 12 months of commit activity for consistency metrics
- Evaluates documentation quality and project complexity

#### 2. **AI & Scoring Engine** (The "Recruiter Brain")
- **Deterministic Scoring**: Weighted metrics across three dimensions:
  - 📚 **Documentation (30%)**: README comprehensiveness and project storytelling
  - ⚙️ **Technical Depth (40%)**: Language diversity and project complexity
  - 📊 **Activity (30%)**: Commit frequency and consistency trends
- **LLM Integration**: Google Gemini AI detects red flags and provides recruiter-focused insights
- Generates: Strong Signals, Red Flags, and Improvement Actions

#### 3. **Presentation Layer** (The Insights Dashboard)
- Beautiful Streamlit dashboard with color-coded metrics
- Visual impact through prominent portfolio score display
- Charts showing language distribution and commit trends
- Actionable feedback presented in easy-to-read format
- Leaderboard of top-analyzed profiles

## 🏗️ Project Structure

```
github-profile-analyzer/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py              # Environment config
│   │   ├── layers/
│   │   │   ├── data_extraction.py     # GitHub data fetching
│   │   │   └── ai_scoring.py          # Scoring + AI insights
│   │   ├── models/
│   │   │   ├── database.py            # SQLAlchemy models
│   │   │   └── schemas.py             # Pydantic models
│   │   ├── api/
│   │   │   └── routes.py              # FastAPI endpoints
│   │   ├── main.py                    # FastAPI app
│   │   └── utils.py                   # Utilities
│   └── pyproject.toml                 # Dependencies
│
├── frontend/
│   ├── app.py                         # Streamlit app
│   ├── components/                    # Reusable components
│   ├── pages/                         # Multi-page structure
│   └── utils/
│       └── api_client.py              # API client
│
├── .env.example                       # Environment template
├── .gitignore
├── pyproject.toml                     # Project config
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- GitHub Personal Access Token ([create here](https://github.com/settings/tokens))
- Google Gemini API Key ([get here](https://makersuite.google.com/app/apikey))
- Poetry (or pip for manual setup)

### 1. Clone & Setup Environment

```bash
# Clone the repository
cd github-profile-analyzer

# Copy environment template
cp .env.example .env

# Edit .env with your tokens
# GITHUB_TOKEN=your_github_token
# GEMINI_API_KEY=your_gemini_api_key
```

### 2. Install Dependencies

**Option A: Using Poetry (Recommended)**
```bash
poetry install
```

**Option B: Using pip**
```bash
pip install -r requirements.txt
```

> **Note:** If you don't have Poetry installed on Windows, run: `pip install poetry` first.

### 3. Start Backend

**Option A: Using Poetry**
```bash
poetry run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Using pip (after running pip install -r requirements.txt)**
```bash
# Navigate to backend directory from project root
cd backend

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option C: Using Windows batch script**
```bash
# From project root
start_backend.bat
```

The API will be available at `http://localhost:8000`
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### 4. Start Frontend

```bash
# From project root
streamlit run frontend/app.py
```

The dashboard will open at `http://localhost:8501`

## 📊 API Endpoints

### Analyze Profile
```
POST /api/analyze?username=<github_username>
```
Returns complete analysis with scores and AI insights.

**Response:**
```json
{
  "username": "torvalds",
  "name": "Linus Torvalds",
  "scores": {
    "total_score": 92.5,
    "documentation_score": 88.0,
    "technical_depth_score": 95.0,
    "activity_score": 90.0
  },
  "ai_insights": {
    "developer_profile": "Systems Engineering Expert",
    "strong_signals": [...],
    "red_flags": [...],
    "improvement_actions": [...]
  },
  "repositories": [...],
  "commit_activity": {...}
}
```

### Get Stored Analysis
```
GET /api/analysis/<username>
```

### Get Leaderboard
```
GET /api/leaderboard?limit=10
```

### Health Check
```
GET /api/health
```

## 🤖 AI Insights Details

The system uses Google Gemini to provide:

### 1. **Developer Profile Categorization**
- Frontend Specialist
- Backend Engineer
- Full-Stack Developer
- Data Scientist
- DevOps Engineer
- etc.

### 2. **Strong Signals** (3 items)
What makes this developer an attractive hire:
- High-quality documentation
- Consistent activity
- Impressive project portfolio
- etc.

### 3. **Red Flags** (3 items)
Potential concerns:
- Sparse commit history
- Missing READMEs
- Lack of recent activity
- etc.

### 4. **Actionable Improvements** (3 items)
Concrete steps to improve hiring discoverability:
- "Add comprehensive README to top repos"
- "Increase GitHub contributions"
- "Document setup instructions"

## 📈 Scoring Breakdown

### Documentation Score (30% weight)
```
- README length > 1000 chars: 100 points
- README length > 500 chars: 75 points
- README length > 100 chars: 50 points
- No README: 25 points
+ 10 point bonus for repo description
```

### Technical Depth Score (40% weight)
```
Language Diversity (40%):
- 1 language: 20 points (max at 5 languages = 100 points)

Project Complexity (60%):
- Stars > 1000: 30 points per repo
- Stars > 100: 20 points per repo
- Stars > 10: 10 points per repo
+ Forks count adds additional points
```

### Activity Score (30% weight)
```
Consistency (70%):
- Active months / Expected months × 100

Commit Frequency (30%):
- Total commits > 1000: 40 points
- Total commits > 500: 30 points
- Total commits > 100: 20 points
- Total commits: 10 points
```

**Final Score** = (Doc × 0.30) + (Tech × 0.40) + (Activity × 0.30)

## 🗄️ Database Schema

### ProfileAnalysis Table
```
- id: Integer (PK)
- username: String (unique)
- name: String
- bio: String
- profile_url: String
- total_score: Float
- documentation_score: Float
- technical_depth_score: Float
- activity_score: Float
- public_repos: Integer
- followers: Integer
- profile_data: JSON
- ai_insights: JSON
- created_at: DateTime
- updated_at: DateTime
```

### AnalysisCache Table
```
- id: Integer (PK)
- username: String (unique)
- raw_profile_data: JSON
- created_at: DateTime
- expires_at: DateTime
- is_valid: Boolean
```

## 🔧 Configuration Options

Edit `.env` file:

```env
# GitHub API
GITHUB_TOKEN=your_token

# Gemini API
GEMINI_API_KEY=your_key

# API Server
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=true

# Database
DATABASE_URL=sqlite:///./github_analyzer.db

# Analysis Settings
MAX_REPOS_ANALYZED=6              # Number of repos to analyze
COMMIT_HISTORY_MONTHS=12          # Months to look back
README_MIN_LENGTH=500             # Min README length for quality
```

## 🐳 Docker Support (Optional)

Build and run with Docker:

```bash
# Build image
docker build -t github-analyzer .

# Run backend
docker run -p 8000:8000 \
  -e GITHUB_TOKEN=your_token \
  -e GEMINI_API_KEY=your_key \
  github-analyzer

# Run frontend
docker run -p 8501:8501 \
  -e API_URL=http://host.docker.internal:8000 \
  github-analyzer streamlit run frontend/app.py
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📝 Example Workflows

### Analyze Your GitHub Profile
```python
import requests

response = requests.get(
    "http://localhost:8000/api/analyze",
    params={"username": "octocat"}
)
analysis = response.json()

print(f"Score: {analysis['scores']['total_score']}")
print(f"Top Strength: {analysis['ai_insights']['strong_signals'][0]['signal']}")
```

### Build Recruiter Dashboard
Use the Streamlit interface at `http://localhost:8501` to:
1. Search for any GitHub profile
2. View portfolio score instantly
3. Review AI insights
4. Check improvement suggestions
5. Browse top profiles on leaderboard

## 🚨 Important Notes

### Rate Limiting
- GitHub API: 60 requests/hour (unauthenticated), 5000/hour (authenticated)
- Gemini API: Check quotas in your Google Cloud project

### Security
- Never commit `.env` file with real tokens
- Use environment variables for all secrets
- Consider adding authentication to the API if deploying publicly

### Performance
- First analysis takes ~5-10 seconds (API calls)
- Subsequent analyses are faster due to caching
- Leaderboard queries are optimized with database indexes

## 📚 Technology Stack

**Backend:**
- FastAPI - Modern async web framework
- PyGithub - GitHub API wrapper
- SQLAlchemy - ORM
- Google Generative AI - LLM integration
- Pydantic - Data validation

**Frontend:**
- Streamlit - Interactive dashboard
- Plotly - Charts and visualizations
- Pandas - Data manipulation
- Requests - HTTP client

**Database:**
- SQLite (development)
- PostgreSQL (production-ready)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - feel free to use and modify

## 🎓 Learning Resources

- [GitHub API Docs](https://docs.github.com/en/rest)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/learn/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Google Gemini API](https://ai.google.dev/)

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Clear cache and reinstall
rm -rf __pycache__
poetry install
```

### GitHub API errors
- Verify token is valid: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`
- Check rate limits: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit`

### Gemini API errors
- Verify API key is correct in `.env`
- Check quota in Google Cloud Console
- Ensure API is enabled

### Streamlit connection issues
- Backend must be running first
- Verify API URL in Streamlit sidebar
- Check no port conflicts (8000, 8501)

## 📞 Support

For issues or questions:
1. Check existing issues on GitHub
2. Review the documentation above
3. Create a new issue with details

---

**Happy analyzing! 🚀**
