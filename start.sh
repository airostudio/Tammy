#!/bin/bash

echo "======================================"
echo "  Tammy AI Assistant - Startup Script"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data logs

# Initialize database
echo "Initializing database..."
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start Tammy, run:"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Or use: make run"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
