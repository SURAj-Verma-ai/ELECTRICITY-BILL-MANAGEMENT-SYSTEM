# EBMS — Electric Bill Management System

A production-grade web application for managing electricity billing, built with Flask. EBMS provides secure user accounts, authentication with self-service password recovery, and a dashboard foundation for tracking and analyzing electric bills — structured from the ground up for real deployment (Docker, CI/CD, monitoring, and infrastructure-as-code included).

## Features

- **Authentication** — registration, login/logout, and change-password flows with hashed credentials
- **Self-service password recovery** — security-question based recovery (no email dependency required)
- **Rate limiting** — brute-force protection on login and recovery endpoints via Flask-Limiter
- **Session-based access control** — `@login_required` route protection and a working dashboard
- **Marketing pages** — home, features, and about pages driven by content modules
- **Database layer** — SQLAlchemy models with Alembic migrations
- **Deployment-ready** — Docker/Docker Compose, Nginx config, Prometheus monitoring, and Terraform/Kubernetes manifests under `infra/`

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLAlchemy ORM, Alembic migrations
- **Security:** Flask-Limiter (rate limiting), hashed passwords, security-question recovery
- **Testing:** Pytest (unit + integration)
- **Infra:** Docker, Docker Compose, Nginx, Prometheus, Terraform, Kubernetes

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for the full directory layout and architectural notes.

## Getting Started

```bash
# Clone and enter the project
git clone https://github.com/<your-username>/ebms.git
cd ebms

# Set up environment
cp .env.example .env
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements/dev.txt

# Run database migrations
alembic upgrade head

# Start the development server
python app.py
```

The app runs on `http://localhost:8000` by default (configurable via `.env`).

## Running Tests

```bash
pytest                  # run all tests
pytest -m unit          # unit tests only
pytest -m integration   # integration tests only
pytest --cov=src        # with coverage
```

## Docker

```bash
docker-compose up -d
```

## License

MIT
