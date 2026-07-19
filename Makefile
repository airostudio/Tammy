.PHONY: help install run test clean docker-build docker-up docker-down format lint

help:
	@echo "Tammy AI Assistant - Available Commands"
	@echo "========================================"
	@echo "install       - Install dependencies"
	@echo "run           - Run the development server"
	@echo "test          - Run tests"
	@echo "format        - Format code with black"
	@echo "lint          - Lint code with flake8"
	@echo "clean         - Clean up generated files"
	@echo "docker-build  - Build Docker image"
	@echo "docker-up     - Start Docker containers"
	@echo "docker-down   - Stop Docker containers"

install:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html

format:
	black app/ tests/ examples/

lint:
	flake8 app/ tests/ examples/ --max-line-length=120

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	rm -f tammy.db

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
