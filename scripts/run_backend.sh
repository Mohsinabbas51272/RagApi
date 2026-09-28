#!/usr/bin/env bash
# Start FastAPI backend
cd "$(dirname "$0")/../backend"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Starting Brillanz FastAPI backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
