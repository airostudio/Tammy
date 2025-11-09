# Tammy - AI Virtual Executive Assistant & Receptionist

Tammy is a comprehensive AI-powered virtual assistant that combines the capabilities of an executive assistant and receptionist into one intelligent bot.

## Features

### Virtual Executive Assistant
- **Calendar & Time Management**: Schedule appointments, manage meetings, send reminders
- **Communication Management**: Email filtering, drafting correspondence, handling inquiries
- **Task & Project Coordination**: Track deadlines, manage to-dos, monitor progress
- **Administrative Support**: Document preparation, expense tracking, travel arrangements
- **Relationship Management**: Contact database, important dates, networking

### Receptionist
- **Call Management**: Answer calls, screen priorities, take messages
- **Visitor Management**: Greet visitors, check-in system, maintain logs
- **Appointment Coordination**: Schedule, confirm, and manage appointments
- **Information Hub**: FAQs, directions, company directory
- **Facility Management**: Book conference rooms, manage resources

### AI Capabilities
- 24/7 Availability
- Multi-channel Support (API, Chat, Email)
- Intelligent Routing & Escalation
- Context Awareness & Memory
- Proactive Assistance
- Natural Language Understanding
- Security & Privacy First

## Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: SQLAlchemy with SQLite (easily upgradable to PostgreSQL)
- **AI/NLP**: OpenAI GPT integration with LangChain
- **Scheduling**: APScheduler
- **Authentication**: JWT tokens
- **API Documentation**: Automatic OpenAPI (Swagger)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Tammy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

Edit `.env` file:
```
DATABASE_URL=sqlite:///./tammy.db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
API_HOST=0.0.0.0
API_PORT=8000
```

### Running the Application

```bash
# Run the development server
python -m uvicorn app.main:app --reload

# Access the API documentation
# Open http://localhost:8000/docs in your browser
```

## API Usage

### Chat with Tammy
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Schedule a meeting with John tomorrow at 2pm"}'
```

### Create an Appointment
```bash
curl -X POST "http://localhost:8000/api/appointments" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "start_time": "2025-11-10T14:00:00",
    "duration_minutes": 60,
    "attendees": ["john@example.com"]
  }'
```

## Architecture

```
tammy/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── appointment.py
│   │   ├── contact.py
│   │   ├── task.py
│   │   ├── visitor.py
│   │   └── message.py
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API endpoints
│   │   ├── appointments.py
│   │   ├── contacts.py
│   │   ├── tasks.py
│   │   ├── visitors.py
│   │   └── chat.py
│   ├── services/            # Business logic
│   │   ├── calendar_service.py
│   │   ├── communication_service.py
│   │   ├── task_service.py
│   │   └── visitor_service.py
│   └── ai/                  # AI integration
│       ├── assistant.py
│       └── intent_parser.py
├── tests/
└── docs/
```

## Features Documentation

### Calendar Management
- Create, update, delete appointments
- Check availability
- Send reminders
- Reschedule conflicts
- Block focus time

### Communication
- Email prioritization
- Draft responses
- Handle routine inquiries
- Meeting agendas
- Message filtering

### Task Management
- Create and track tasks
- Set deadlines
- Monitor progress
- Follow-ups
- Team coordination

### Visitor Management
- Check-in/check-out
- Visitor logs
- Badge management
- Notifications

### Natural Language Interface
Tammy understands natural requests like:
- "Schedule a meeting with Sarah next Tuesday at 3pm"
- "Who's my next appointment?"
- "Remind me to call John in 2 hours"
- "Check in visitor Jane Doe"
- "What tasks are due today?"

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
# Format code
black app/

# Lint
flake8 app/
```

## Security

- JWT-based authentication
- API key management
- Data encryption at rest
- HTTPS required in production
- Rate limiting
- Input validation

## Deployment

### Docker
```bash
docker-compose up -d
```

### Production Checklist
- [ ] Set strong SECRET_KEY
- [ ] Configure production database (PostgreSQL)
- [ ] Enable HTTPS
- [ ] Set up API rate limiting
- [ ] Configure backup strategy
- [ ] Enable logging and monitoring
- [ ] Set up alerting

## Contributing

Contributions are welcome! Please read our contributing guidelines.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
