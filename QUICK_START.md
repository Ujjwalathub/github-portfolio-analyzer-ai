# ⚡ Quick Start Guide - GitHub Profile Analyzer

A step-by-step guide to get your GitHub Profile Analyzer running in minutes.

---

## 📋 Prerequisites

- **Python 3.9+** installed
- **Git** installed
- A **GitHub account** (for API token)
- Optionally: A **Google Gemini** account (for AI features)

---

## 🚀 5-Minute Setup

### Step 1: Get Your API Keys (2 minutes)

#### GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" (classic)
3. **Name:** GitHub Profile Analyzer
4. **Scopes:** Select `repo`, `user`, `gist`, `read:org`
5. Click "Generate token" and **copy the token** (you won't see it again!)

#### Google Gemini API Key (Optional but Recommended)
1. Go to https://aistudio.google.com/app/apikeys
2. Click "Create API Key"
3. Copy the key

### Step 2: Configure Environment (1 minute)

In the project root directory:

```bash
# Copy and edit the example file
cp .env.example .env
```

Edit `.env` and fill in your keys:
```env
GITHUB_TOKEN=ghp_xxxxx...        # Your GitHub token
GEMINI_API_KEY=AIza...            # Your Gemini key (optional)
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Install Dependencies (1 minute)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Start Backend (1 minute)

**In Terminal 1:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 5: Start Frontend

**In Terminal 2:**
```bash
# Activate venv if not already activated
streamlit run frontend/app.py
```

Your browser should open to `http://localhost:8501` 🎉

---

## ✅ Verify Everything Works

### Test 1: API Health Check
```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"healthy","environment":"development"}`

### Test 2: Analyze a Profile

In the Streamlit UI:
1. Enter a GitHub username or full URL: `https://github.com/torvalds`
2. Click "Analyze Profile"
3. Wait 10-30 seconds
4. View results!

Or via curl:
```bash
curl "http://localhost:8000/api/analyze?username=torvalds"
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'app'` | Make sure you're in `backend` directory when running uvicorn |
| `500 Internal Server Error` | Check backend terminal for error details - usually missing API key |
| `Cannot connect to backend` | Ensure backend is running on port 8000 |
| `Streamlit not found` | Run `pip install -r requirements.txt` |
| `GitHub profile not found` | Ensure the username exists and is public |

### View Detailed Error Logs

The backend terminal shows every error. If you get a 500 error in Streamlit, check the backend terminal for:
- `GitHub API error` → Invalid token or rate limit
- `Unable to fetch profile` → Username doesn't exist
- `Error analyzing profile` → Scroll up for root cause

---

## 📝 What Gets Analyzed

For each GitHub profile, the system calculates:

- **📚 Documentation Score** (30%): README quality, project descriptions
- **⚙️ Technical Depth** (40%): Languages used, project complexity
- **📊 Activity Score** (30%): Commit frequency, consistency
- **AI Insights** (if Gemini API key set): Strong signals, red flags, improvements

---

## 🎯 Next Steps

1. **Explore the UI**: Try analyzing different profiles
2. **Check the Leaderboard**: See top-scored profiles
3. **Read the Docs**: See [FIXES_AND_SETUP.md](FIXES_AND_SETUP.md) for detailed info
4. **Create a Demo**: Record a 5-minute walkthrough
5. **Deploy**: See [DEVELOPMENT.md](DEVELOPMENT.md) for deployment options

---

## 📊 File Locations

| Component | Location |
|-----------|----------|
| Backend main app | `backend/app/main.py` |
| API routes | `backend/app/api/routes.py` |
| Frontend | `frontend/app.py` |
| Config | `backend/app/core/config.py` |
| Database models | `backend/app/models/database.py` |

---

## 🔑 Environment Variables Reference

```env
# Required
GITHUB_TOKEN=your_token_here          # GitHub API token

# Optional but recommended
GEMINI_API_KEY=your_key_here          # For AI insights

# Server config (defaults are fine)
API_HOST=0.0.0.0                      # Bind address
API_PORT=8000                         # Listen port
API_RELOAD=true                       # Auto-reload on changes

# Database
DATABASE_URL=sqlite:///./github_analyzer.db

# Analysis
MAX_REPOS_ANALYZED=6                  # Repos to analyze per user
COMMIT_HISTORY_MONTHS=12              # History window
```

---

## ⚙️ Common Tasks

### Check if Backend is Running
```bash
curl http://localhost:8000/
```

### View API Documentation
Open: http://localhost:8000/docs

### Reset Database
```bash
rm github_analyzer.db
```

### Test URL Parsing
```bash
# These should all work:
curl "http://localhost:8000/api/analyze?username=torvalds"
curl "http://localhost:8000/api/analyze?username=github.com/torvalds"
curl "http://localhost:8000/api/analyze?username=https://github.com/torvalds"
```

---

## 🆘 Still Having Issues?

1. **Check .env file** - Verify it exists and has `GITHUB_TOKEN` set
2. **Check backend logs** - Terminal output shows the actual error
3. **Use test script** - Run `python test_backend.py` from project root
4. **Review FIXES_AND_SETUP.md** - Detailed troubleshooting guide

---

## 📚 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [GitHub API](https://docs.github.com/en/rest)
- [Google Gemini API](https://ai.google.dev/)

---

**Ready? Start with Step 1 above! You'll be running in 5 minutes.** 🚀
