# Bible API

A modern REST API for accessing Bible translations with powerful search and content retrieval capabilities.

## Getting Started

### Prerequisites

- Docker & Docker Compose
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
# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Start database only
docker-compose up -d db

# Update .env
# POSTGRES_HOST=localhost

# Run migrations/load data
python -m src.loaders

# Start API
uvicorn src.main:app --reload
```

