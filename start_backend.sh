#!/bin/bash
# Start backend server

echo "Starting GitHub Profile Analyzer Backend..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
