# FastAPI Boilerplate

A minimal and opinionated FastAPI boilerplate for building scalable, production-ready APIs.

## Features
- FastAPI with async support
- Structured project layout
- Pydantic models for validation
- SQLAlchemy for managing DB models
- Albemic for managing migrations
- Dependency injection
- Environment-based configuration
- Automatic interactive API docs (Swagger & ReDoc)
- Authentication

## Getting Started

### 1. Create Virtual Environment
```bash
venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Run migrations
```bash
alembic revision --autogenerate -m 'MESSAGE' # for a new project
alembic upgrade head
alembic current # to check things went smoothly 
```

### 4. Run the server
```bash
fastapi dev 
```

## Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc