# EBMS Project Structure Documentation

## Directory Hierarchy

```
EBMS/
├── src/                                  # Source code
│   ├── core/                            # Core business logic
│   ├── api/                             # REST API routes & endpoints
│   ├── services/                        # Business logic & services
│   ├── models/                          # Database models (SQLAlchemy)
│   ├── utils/                           # Helper functions & utilities
│   ├── middleware/                      # Custom middleware
│   └── __init__.py
│
├── tests/                               # Test suite
│   ├── unit/                            # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── ...
│   ├── integration/                     # Integration tests
│   │   ├── test_api.py
│   │   ├── test_database.py
│   │   └── ...
│   ├── fixtures/                        # Test data & fixtures
│   │   ├── users.py
│   │   ├── bills.py
│   │   └── ...
│   ├── conftest.py                     # Pytest configuration
│   └── __init__.py
│
├── config/                              # Configuration management
│   ├── config.py                       # Main configuration file
│   ├── logging_config.py                # Logging setup
│   ├── environments/                   # Environment-specific configs
│   │   ├── development.yml
│   │   ├── testing.yml
│   │   └── production.yml
│   └── schemas/                         # Config schemas
│
├── database/                            # Database layer
│   ├── migrations/                     # Alembic migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── seeds/                          # Seed data
│   │   ├── users.sql
│   │   ├── bills.sql
│   │   └── ...
│   └── schema.sql                      # Database schema
│
├── docs/                                # Documentation
│   ├── architecture/                   # Architecture guides
│   │   └── ARCHITECTURE.md
│   ├── api/                            # API documentation
│   │   ├── API_SPEC.md
│   │   └── endpoints/
│   └── guides/                         # Setup & how-to guides
│       ├── INSTALLATION.md
│       └── DEPLOYMENT.md
│
├── scripts/                             # Utility scripts
│   ├── maintenance/                    # Maintenance scripts
│   │   ├── backup.sh
│   │   ├── cleanup.sh
│   │   └── ...
│   ├── deployment/                    # Deployment scripts
│   │   ├── deploy.sh
│   │   └── rollback.sh
│   └── dev/                            # Development scripts
│       ├── setup.sh
│       ├── seed_db.sh
│       └── ...
│
├── .github/                            # GitHub configuration
│   └── workflows/                      # CI/CD workflows
│       ├── ci-cd.yml
│       ├── deploy.yml
│       └── security.yml
│
├── docker/                             # Docker configuration
│   ├── app/                            # Application Dockerfile
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   ├── nginx/                          # Nginx configuration
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   └── docker-compose.override.yml    # Development override
│
├── logs/                               # Application logs
│   ├── app.log
│   ├── error.log
│   ├── access.log
│   └── archived/
│
├── monitoring/                         # Monitoring & alerting
│   ├── prometheus/                    # Prometheus configuration
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   └── logs/                          # Log aggregation
│       └── fluent-bit.conf
│
├── infra/                              # Infrastructure as Code
│   ├── terraform/                     # Terraform configurations
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── k8s/                           # Kubernetes manifests
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml
│
├── requirements/                       # Python dependencies
│   ├── prod.txt                        # Production dependencies
│   ├── dev.txt                         # Development dependencies
│   ├── test.txt                        # Testing dependencies (optional)
│   └── constraints.txt                 # Dependency constraints
│
├── templates/                          # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   └── ...
│
├── static/                             # Static assets
│   ├── css/
│   ├── js/
│   ├── images/
│   └── ...
│
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── .dockerignore                       # Docker ignore rules
├── docker-compose.yml                  # Docker Compose configuration
├── pytest.ini                          # Pytest configuration
├── pyproject.toml                      # Python project metadata
├── CONTRIBUTING.md                     # Contribution guidelines
├── PROJECT_STRUCTURE.md                # This file
├── README.md                           # Project README
├── LICENSE                             # License file
└── app.py                              # Application entry point
```

## Key Directories Explained

### `src/` - Source Code
The heart of the application, organized by function:
- **core/**: Core business logic, shared utilities
- **api/**: REST API route definitions and request/response handling
- **services/**: Business logic, calculations, external integrations
- **models/**: SQLAlchemy ORM models
- **utils/**: Helper functions, validators, formatters
- **middleware/**: Authentication, logging, error handling

### `tests/` - Test Suite
Comprehensive testing structure:
- **unit/**: Fast, isolated unit tests
- **integration/**: Tests involving database, external services
- **fixtures/**: Shared test data, factories

### `config/` - Configuration
Centralized configuration management:
- Environment-based configs (dev, test, prod)
- Logging configuration
- Schema validation for configs

### `database/` - Database Management
Database schema and data management:
- **migrations/**: Alembic version control for schema changes
- **seeds/**: Initial/reference data scripts

### `docs/` - Documentation
Comprehensive documentation:
- Architecture decisions
- API specifications
- Setup and deployment guides

### `scripts/` - Automation
Operational scripts:
- Development setup
- Maintenance tasks
- Deployment automation

### `.github/workflows/` - CI/CD
GitHub Actions automation:
- Testing pipeline
- Deployment workflows
- Security scanning

### `docker/` - Containerization
Docker configuration:
- Multi-stage builds for optimization
- Docker Compose for local development
- Nginx reverse proxy configuration

### `monitoring/` - Observability
Monitoring and alerting:
- Prometheus metrics configuration
- Alert rules
- Log aggregation setup

### `infra/` - Infrastructure
Infrastructure as Code:
- Terraform for cloud resources
- Kubernetes manifests for orchestration

## File Descriptions

### Core Files
| File | Purpose |
|------|---------|
| `app.py` | Application entry point, Flask app initialization |
| `pyproject.toml` | Python project metadata, dependencies |
| `requirements/*.txt` | Pip requirements for different environments |
| `.env.example` | Environment variable template |

### Configuration Files
| File | Purpose |
|------|---------|
| `pytest.ini` | Pytest configuration and markers |
| `docker-compose.yml` | Local development services orchestration |
| `.gitignore` | Git ignore patterns |
| `.dockerignore` | Docker build ignore patterns |

### Documentation Files
| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick start |
| `CONTRIBUTING.md` | Development guidelines |
| `PROJECT_STRUCTURE.md` | This file - directory structure |
| `docs/architecture/ARCHITECTURE.md` | Detailed architecture guide |
| `docs/api/API_SPEC.md` | API endpoints specification |

## Development Workflow

### Local Setup
```bash
# Setup environment
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt

# Start services
docker-compose up -d

# Run migrations
alembic upgrade head

# Start development server
python app.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test type
pytest -m unit
pytest -m integration

# With coverage
pytest --cov=src
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

## Scalability Features

1. **Modular Architecture**: Clear separation of concerns
2. **Database Optimization**: Connection pooling, indexing strategies
3. **Caching Layer**: Redis for frequently accessed data
4. **Async Processing**: Celery for background tasks
5. **Load Balancing**: Nginx reverse proxy configuration
6. **Containerization**: Docker for consistent environments
7. **Horizontal Scaling**: Stateless API services
8. **Monitoring**: Prometheus metrics and alerting

## Security Considerations

- Environment-based secrets management
- JWT authentication for APIs
- Database transaction safety (ACID)
- Input validation and sanitization
- Rate limiting for API protection
- Non-root container user
- TLS/HTTPS support

## Maintainability Features

- Consistent code style (Black, isort)
- Type hints support (mypy)
- Comprehensive logging
- Structured error responses
- Database migrations
- API documentation
- Contributing guidelines

## Future Expansion Points

1. **Microservices**: Split services into independent modules
2. **GraphQL**: Add GraphQL API alongside REST
3. **Real-time**: WebSocket support for live updates
4. **Analytics**: Data warehouse for business intelligence
5. **ML/AI**: Predictive billing and anomaly detection
6. **Mobile**: Native iOS/Android applications

---

For more details on specific aspects, refer to:
- Architecture: `docs/architecture/ARCHITECTURE.md`
- API: `docs/api/API_SPEC.md`
- Contribution: `CONTRIBUTING.md`
- Development: Individual `README.md` files in subdirectories
