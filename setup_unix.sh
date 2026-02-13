#!/bin/bash
# GitHub Profile Analyzer - Complete Setup & Run Script for macOS/Linux
# This script handles all setup steps and launches the backend

set -e  # Exit on error

echo ""
echo "============================================================"
echo "  GitHub Profile Analyzer - macOS/Linux Setup Script"
echo "============================================================"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "ERROR: This script must be run from the project root directory"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "[2/5] Setting up .env file..."
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo "Created .env file from template"
    else
        echo "WARNING: .env.example not found. Creating minimal .env..."
        cat > .env << EOF
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
EOF
    fi
    
    echo ""
    echo "IMPORTANT: Edit .env and add your API keys:"
    echo "  GITHUB_TOKEN=your_github_token_here"
    echo "  GEMINI_API_KEY=your_gemini_api_key_here (optional)"
    echo ""
    echo "Get tokens from:"
    echo "  - GitHub: https://github.com/settings/tokens"
    echo "  - Gemini: https://aistudio.google.com/app/apikeys"
    echo ""
else
    echo "[2/5] .env file already exists"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "[3/5] Creating Python virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created successfully"
else
    echo ""
    echo "[3/5] Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[4/5] Activating virtual environment and installing dependencies..."
source venv/bin/activate

# Install requirements
pip install -q -r requirements.txt
echo "Dependencies installed successfully"

# Display next steps
echo ""
echo "============================================================"
echo "[5/5] Setup Complete!"
echo "============================================================"
echo ""
echo "Your system is ready to run the GitHub Profile Analyzer!"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. EDIT YOUR .env FILE"
echo "   Edit .env and add your API keys:"
echo "     GITHUB_TOKEN=ghp_xxxxx..."
echo "     GEMINI_API_KEY=AIza... (optional)"
echo ""
echo "2. START THE BACKEND"
echo "   Run this command:"
echo "     source venv/bin/activate"
echo "     cd backend"
echo "     python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. START THE FRONTEND (in another terminal)"
echo "   Run:"
echo "     source venv/bin/activate"
echo "     streamlit run frontend/app.py"
echo ""
echo "4. OPEN YOUR BROWSER"
echo "   Navigate to: http://localhost:8501"
echo ""
echo "DOCUMENTATION:"
echo "   - Quick Start: QUICK_START.md"
echo "   - Setup Guide: FIXES_AND_SETUP.md"
echo "   - Development: DEVELOPMENT.md"
echo ""
echo "============================================================"
echo ""

# Ask if user wants to start the backend now
read -p "Do you want to start the backend now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting backend..."
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo ""
    echo "Remember to start the backend before using the frontend!"
    echo ""
fi
