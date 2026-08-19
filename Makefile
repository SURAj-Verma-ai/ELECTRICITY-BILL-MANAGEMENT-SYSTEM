.PHONY: help install setup dev test lint format clean migrate docker-build docker-up docker-down docker-logs

help:
	@echo "EBMS - Electric Bill Management System"
	@echo ""
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make setup            - Setup development environment"
	@echo "  make dev              - Start development server"
	@echo "  make test             - Run tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo "  make lint             - Run code quality checks"
	@echo "  make format           - Format code with black and isort"
	@echo "  make migrate          - Run database migrations"
	@echo "  make seed-db          - Seed database with sample data"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker services"
	@echo "  make docker-down      - Stop Docker services"
	@echo "  make docker-logs      - View Docker logs"
	@echo "  make docs             - Generate documentation"

# Installation and Setup
install:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements/prod.txt

install-dev:
	pip install --upgrade pip setuptools wheel
	pip install -r requirements/dev.txt

setup: install-dev
	pre-commit install
	cp .env.example .env
	@echo "✓ Development environment setup complete"

# Development
dev:
	python app.py

shell:
	flask shell

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v -m unit

test-integration:
	pytest tests/integration/ -v -m integration

test-coverage:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "✓ Coverage report generated in htmlcov/index.html"

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 src/ tests/ --max-line-length=100
	@echo "Running mypy..."
	mypy src/ --ignore-missing-imports
	@echo "✓ All linting checks passed"

format:
	@echo "Running black..."
	black src/ tests/ config/
	@echo "Running isort..."
	isort src/ tests/ config/
	@echo "✓ Code formatted successfully"

check: lint
	@echo "✓ All checks passed"

# Database
migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-down:
	alembic downgrade -1

seed-db:
	python scripts/dev/seed_db.py

reset-db: migrate-down migrate seed-db
	@echo "✓ Database reset complete"

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Application: http://localhost:8000"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

docker-ps:
	docker-compose ps

# Documentation
docs:
	cd docs && sphinx-build -b html . _build
	@echo "✓ Documentation built in docs/_build/index.html"

# Cleanup
clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .egg-info -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "✓ Cleanup complete"

# Full workflow
all: clean install-dev lint test
	@echo "✓ All checks passed"

.DEFAULT_GOAL := help
