# Quick Start Guide - GitHub Profile Analyzer

## Prerequisites
- Python 3.8+ installed
- Git installed
- Virtual environment created and activated

## Step 1: Install Dependencies
```bash
cd github-profile-analyzer
pip install -r requirements.txt
```

## Step 2: Verify .env File
Ensure `.env` exists in the root directory with:
```
```

## Step 3: Start the Backend API

### Option A: Direct Command
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Option B: Using Batch Script (Windows)
```bash
.\start_backend.bat
```

### Option C: Using Shell Script (Unix/macOS)
```bash
./start_backend.sh
```

## Step 4: Start the Frontend (Optional)

### Option A: Direct Command
```bash
cd frontend
streamlit run app.py
```

### Option B: Using Batch Script (Windows)
```bash
.\start_frontend.bat
```

### Option C: Using Shell Script (Unix/macOS)
```bash
./start_frontend.sh
```

## Accessing the Application

### Backend API
- **Swagger Docs**: http://127.0.0.1:8000/docs
- **API Root**: http://127.0.0.1:8000/
- **Analyze Endpoint**: http://127.0.0.1:8000/api/analyze?username={github_username}

### Frontend (if running)
- **App**: http://localhost:8501

## Testing the API

### Using Swagger UI
1. Visit http://127.0.0.1:8000/docs
2. Click on "GET /api/analyze"
3. Click "Try it out"
4. Enter a GitHub username (e.g., "torvalds", "octocat")
5. Click "Execute"

### Using cURL
```bash
# Analyze a GitHub user
curl "http://127.0.0.1:8000/api/analyze?username=torvalds"

# Pretty print the response
curl -s "http://127.0.0.1:8000/api/analyze?username=octocat" | python -m json.tool
```

### Using PowerShell
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/analyze?username=octocat" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution**: Make sure you're running from the `backend/` directory:
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Issue: "GitHub API token not configured"
**Solution**: Verify `.env` file exists in the root directory with GITHUB_TOKEN value

### Issue: Port 8000 Already in Use
**Solution**: Use a different port:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

### Issue: Token Not Loading
**Solution**: Test directly:
```bash
cd backend
python -c "from app.core.config import settings; print('Token loaded:', bool(settings.github_token))"
```

## Project Structure
```
github-profile-analyzer/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── layers/         # Data extraction & AI scoring
│   │   ├── models/         # Database & schemas
│   │   └── main.py         # FastAPI app
│   └── .env                # Environment variables (backup)
├── frontend/               # Streamlit frontend
│   ├── app.py              # Main app
│   ├── components/         # UI components
│   ├── pages/              # Pages (if multi-page)
│   └── utils/              # Utilities
├── .env                    # Environment variables (root)
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Key Files for Token Loading

| File | Purpose |
|------|---------|
| `.env` (root) | Environment variables |
| `backend/.env` | Backup .env file |
| `backend/app/core/config.py` | Configuration & token loading |
| `backend/app/main.py` | FastAPI app & validation |

## Next Steps

1. **Test Backend**: Visit http://127.0.0.1:8000/docs
2. **Run Analysis**: Test with different GitHub usernames
3. **Review Scores**: Check the scoring system
4. **Collect Feedback**: Review generated insights
5. **Refine**: Improve recommendations if needed
6. **Demo**: Record walkthrough video
7. **Submit**: Ensure repo is public and submit link

## Support

For issues or questions:
1. Check logs for error messages
2. Verify .env file configuration
3. Test with known GitHub usernames (torvalds, octocat, gvanrossum)
4. Review API documentation at http://localhost:8000/docs

Happy coding! 🚀


