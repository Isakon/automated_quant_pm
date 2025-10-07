#!/bin/bash

# Run Server Script for Automated Quant PM
# This script starts the FastAPI server with proper configuration

echo "🚀 Starting Automated Quant PM Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f "credentials/.env" ]; then
    echo "⚠️  credentials/.env not found. Creating from template..."
    if [ -f "credentials/.env.example" ]; then
        cp credentials/.env.example credentials/.env
        echo "✅ Created credentials/.env - Please add your API keys!"
    else
        echo "❌ credentials/.env.example not found!"
        exit 1
    fi
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/models

# Development mode with uvicorn (hot reload)
echo "📡 Starting development server with auto-reload..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

# For production, use gunicorn with uvicorn workers:
# gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000