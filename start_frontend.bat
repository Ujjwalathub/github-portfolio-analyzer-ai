@echo off
REM Start frontend dashboard (Windows)
REM This script must be in the project root directory

cd /d "%~dp0"
echo Current directory: %cd%

if not exist "frontend" (
    echo Error: frontend folder not found!
    echo Make sure this script is in: E:\Github\github-profile-analyzer\
    pause
    exit /b 1
)

echo Entering project directory: %cd%

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

echo Starting frontend on http://localhost:8501
streamlit run frontend/app.py
pause
