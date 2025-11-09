# Contributing to Tammy AI Assistant

Thank you for your interest in contributing to Tammy! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Tammy
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the development server:
```bash
python -m uvicorn app.main:app --reload
```

## Development Workflow

### Code Style

We follow PEP 8 style guidelines with these tools:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Format your code before committing:
```bash
make format
make lint
```

### Writing Tests

We use pytest for testing. All new features should include tests:

```python
# tests/test_feature.py
import pytest

@pytest.mark.asyncio
async def test_new_feature():
    """Test description"""
    # Test implementation
    pass
```

Run tests:
```bash
make test
```

### Commit Guidelines

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```bash
git commit -m "feat: add visitor notification system"
git commit -m "fix: resolve appointment scheduling conflict"
```

## Project Structure

```
tammy/
├── app/
│   ├── api/          # API endpoints
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── ai/           # AI/NLP integration
│   └── utils/        # Utility functions
├── tests/            # Test files
├── examples/         # Example usage
└── docs/             # Documentation
```

## Adding New Features

### 1. Plan Your Feature

- Check existing issues or create a new one
- Discuss the approach with maintainers
- Break down into smaller tasks

### 2. Implement

Follow this order:
1. Create database model (if needed) in `app/models/`
2. Create Pydantic schema in `app/schemas/`
3. Implement service logic in `app/services/`
4. Add API endpoints in `app/api/`
5. Write tests in `tests/`
6. Update documentation

### 3. Testing

Test your changes thoroughly:
- Unit tests for individual functions
- Integration tests for API endpoints
- Manual testing with example scripts

### 4. Documentation

Update relevant documentation:
- Add docstrings to all functions/classes
- Update README.md if needed
- Add examples to `examples/`
- Update API documentation

## Pull Request Process

1. **Create a branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
- Follow code style guidelines
- Write tests
- Update documentation

3. **Test your changes:**
```bash
make test
make lint
```

4. **Commit and push:**
```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/your-feature-name
```

5. **Open a Pull Request:**
- Provide a clear description
- Reference related issues
- Include screenshots if applicable
- Wait for review

## Code Review

All submissions require review. We look for:

- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations

## Areas for Contribution

### High Priority

- [ ] Integration with external calendar services (Google Calendar, Outlook)
- [ ] Email integration (SMTP, IMAP)
- [ ] SMS/Voice integration (Twilio)
- [ ] Advanced NLP with OpenAI GPT
- [ ] Multi-language support
- [ ] Mobile app integration

### Features

- [ ] Recurring appointments and tasks
- [ ] Team collaboration features
- [ ] Advanced reporting and analytics
- [ ] Custom workflows
- [ ] Plugin system

### Improvements

- [ ] Performance optimization
- [ ] Better error handling
- [ ] Enhanced security
- [ ] Improved documentation
- [ ] More test coverage

## Getting Help

- Check the documentation
- Search existing issues
- Ask in discussions
- Join our community chat

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make Tammy better for everyone. We appreciate your time and effort!
