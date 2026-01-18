# Bible API

A modern REST API for accessing Bible translations with powerful search and content retrieval capabilities.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- (Optional) Make for convenience commands

### Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:bsp-org/backend.git
   cd backend
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Load Bible data**
   ```bash
   docker-compose exec app python -m src.loaders
   ```

5. **Verify**
   ```bash
   curl http://localhost:8000/health
   ```

### API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### List Translations
```bash
curl http://localhost:8000/api/translations
```

For all endpoints, check the docs.

## Development

### Local Setup (without Docker)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Start database only
docker-compose up -d db

# Update .env
# POSTGRES_HOST=localhost

# Run migrations/load data
uv run python -m src.loaders

# Start API
uv run uvicorn src.main:app --reload
```

### Using Make Commands

The project includes a Makefile for common development tasks:

- `make install` - Install dependencies
- `make run` - Run the development server
- `make test` - Run tests
- `make lint` - Run linting checks
- `make fmt` - Format code
- `make type` - Run type checking
- `make cov` - Run tests with coverage report
- `make precommit-install` - Install pre-commit hooks

