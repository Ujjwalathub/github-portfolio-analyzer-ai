@echo off
REM GitHub Profile Analyzer - Complete Setup & Run Script for Windows
REM This script handles all setup steps and launches both backend and frontend

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ==============================================================
echo  GitHub Profile Analyzer - Windows Setup Script
echo ==============================================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ERROR: This script must be run from the project root directory
    echo Expected: E:\Github\github-profile-analyzer\
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo [2/5] Setting up .env file...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo Created .env file from template
        echo.
        echo IMPORTANT: Edit .env and add your API keys:
        echo   GITHUB_TOKEN=your_github_token_here
        echo   GEMINI_API_KEY=your_gemini_api_key_here (optional)
        echo.
        echo Get tokens from:
        echo   - GitHub: https://github.com/settings/tokens
        echo   - Gemini: https://aistudio.google.com/app/apikeys
        echo.
        pause
    ) else (
        echo WARNING: .env.example not found. Creating minimal .env...
        (
            echo GITHUB_TOKEN=your_github_token_here
            echo GEMINI_API_KEY=your_gemini_api_key_here
            echo API_HOST=0.0.0.0
            echo API_PORT=8000
        ) > .env
    )
) else (
    echo [2/5] .env file already exists
)

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [3/5] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo [3/5] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [4/5] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

REM Install requirements
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully

REM Display next steps
echo.
echo ============================================================
echo [5/5] Setup Complete!
echo ============================================================
echo.
echo Your system is ready to run the GitHub Profile Analyzer!
echo.
echo NEXT STEPS:
echo.
echo 1. EDIT YOUR .env FILE
echo    Open .env and add your API keys:
echo      GITHUB_TOKEN=ghp_xxxxx...
echo      GEMINI_API_KEY=AIza... (optional)
echo.
echo 2. START THE BACKEND
echo    Open a new terminal (Ctrl+` in VS Code) and run:
echo      cd backend
echo      python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 3. START THE FRONTEND
echo    In this terminal, run:
echo      streamlit run frontend/app.py
echo.
echo 4. OPEN YOUR BROWSER
echo    The frontend will open automatically at: http://localhost:8501
echo.
echo DOCUMENTATION:
echo   - Quick Start: QUICK_START.md
echo   - Setup Guide: FIXES_AND_SETUP.md
echo   - Development: DEVELOPMENT.md
echo   - API Docs: Visit http://localhost:8000/docs when running
echo.
echo ==============================================================
echo.

REM Ask if user wants to start the backend now
set /p start_backend="Do you want to start the backend now? (y/n): "
if /i "%start_backend%"=="y" (
    echo.
    echo Starting backend...
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo.
    echo Remember to start the backend before using the frontend!
    echo.
    pause
)
