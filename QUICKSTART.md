# Quick Start Guide - ENDCOM.NET AI Assistant

Get ENDCOM.NET up and running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- pip package manager

## Installation (Choose One)

### Option 1: Automatic Setup (Recommended)

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up configuration
- Initialize the database

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your settings (optional for basic use)

# 4. Create directories
mkdir -p data logs
```

## Running ENDCOM.NET

### Start the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the Makefile:
```bash
make run
```

### Access the API

Open your browser to:
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Basic Info**: http://localhost:8000

## Try It Out!

### 1. Interactive Chat Demo

In a new terminal:
```bash
source venv/bin/activate  # Activate venv first
python examples/chat_demo.py
```

Then try:
- "What can you help me with?"
- "Schedule a meeting tomorrow at 2pm"
- "Show my tasks"
- "Create a task to review proposal"

### 2. API Examples

```bash
python examples/example_usage.py
```

### 3. Using the REST API

```bash
# Chat with Tammy
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What appointments do I have?"}'

# Get capabilities
curl http://localhost:8000/api/chat/capabilities

# Create an appointment
curl -X POST http://localhost:8000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": "Team Meeting",
    "start_time": "2025-11-15T14:00:00",
    "duration_minutes": 60
  }'
```

## What Tammy Can Do

Ask Tammy to:

**Calendar & Appointments:**
- "Schedule a meeting with John tomorrow at 2pm"
- "What's on my calendar today?"
- "Cancel my 3pm meeting"

**Tasks:**
- "Create a task to call Sarah"
- "Show my high priority tasks"
- "What tasks are due today?"

**Contacts:**
- "Add contact John Doe, email john@example.com"
- "Find contact for Acme Corp"
- "Show all my contacts"

**Visitors:**
- "Check in visitor Jane Smith"
- "Who is currently checked in?"
- "Schedule visitor appointment for tomorrow"

**Messages:**
- "Show unread messages"
- "What emails need a response?"

## Configuration (Optional)

Edit `.env` file for:

- **Database**: Change from SQLite to PostgreSQL
- **OpenAI**: Add API key for enhanced AI features
- **Email**: Configure SMTP for email integration
- **Twilio**: Add credentials for SMS/call features

## Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Troubleshooting

**Import errors?**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Port already in use?**
```bash
# Use a different port
python -m uvicorn app.main:app --reload --port 8001
```

**Database errors?**
```bash
# Delete and recreate database
rm tammy.db
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
```

## Next Steps

1. Explore the API documentation at http://localhost:8000/docs
2. Try the interactive examples
3. Read the full [API Documentation](API_DOCUMENTATION.md)
4. Check out [Contributing Guidelines](CONTRIBUTING.md)

## Need Help?

- Check the full [README.md](README.md)
- Review [API Documentation](API_DOCUMENTATION.md)
- Open an issue on GitHub

Enjoy using Tammy! 🎉
