@echo off
REM Start backend server (Windows)
REM This script must be in the project root directory

cd /d "%~dp0"
echo Current directory: %cd%

if not exist "backend" (
    echo Error: backend folder not found!
    echo Make sure this script is in: E:\Github\github-profile-analyzer\
    pause
    exit /b 1
)

cd backend
echo Entering backend directory: %cd%

REM Activate virtual environment if it exists
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
    echo Virtual environment activated
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

echo Starting backend server on http://0.0.0.0:8000
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
