# Development Guide

This guide covers development setup, coding standards, and best practices for the Nitty service.

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- UV package manager
- Git

### Initial Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd nitty
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Set up environment**

   ```bash
   cp .env.example .env
   # Edit .env with your local database credentials
   ```

4. **Set up database**

   ```bash
   # Start PostgreSQL (using Docker)
   docker run --name nitty-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=nitty_dev -p 5432:5432 -d postgres:15

   # Run migrations
   alembic upgrade head
   ```

5. **Start development server**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Project Structure

```bash
app/
├── auth/                    # Authentication module
│   ├── __init__.py
│   ├── models.py           # User models and schemas
│   ├── router.py           # Auth endpoints
│   └── service.py          # Auth business logic
├── communities/            # Community management
│   ├── __init__.py
│   ├── models.py           # Community models
│   ├── router.py           # Community endpoints
│   └── service.py          # Community business logic
├── events/                 # Event management
│   ├── __init__.py
│   ├── models.py           # Event models
│   ├── router.py           # Event endpoints
│   └── service.py          # Event business logic
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Test configuration
│   ├── test_user.py        # User tests
│   └── utils.py            # Test utilities
├── config.py               # Application configuration
├── database.py             # Database connection
├── deps.py                 # Dependencies (auth, etc.)
├── main.py                 # FastAPI application
└── tests_pre_start.py      # Pre-start tests
```

## Coding Standards

### Python Style

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Import order**: isort configuration
- **Type hints**: Required for all functions
- **Docstrings**: Google style for all public functions

### Code Formatting

```bash
# Format code with Black
black app/

# Sort imports with isort
isort app/

# Check formatting
black --check app/
isort --check-only app/
```

### Type Checking

```bash
# Run type checking with mypy
mypy app/

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Linting

```bash
# Run flake8
flake8 app/

# Configuration in .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,migrations
```

## Database Development

### Models

Models are defined using SQLModel (Pydantic + SQLAlchemy):

```python
from sqlmodel import Field, Relationship
from app.database import NittySQLModel

class User(NittySQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    # ... other fields
```

### Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new field to user table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current revision
alembic current
```

### Database Seeding

Create seed data for development:

```python
# scripts/seed_data.py
from app.database import get_db
from app.auth.service import create_user
from app.auth.models import UserCreate

def seed_users():
    session = next(get_db())

    users = [
        UserCreate(
            email="admin@example.com",
            password="admin123",
            full_name="Admin User",
            is_superuser=True
        ),
        UserCreate(
            email="user@example.com",
            password="user123",
            full_name="Regular User"
        )
    ]

    for user_data in users:
        create_user(session=session, user_create=user_data)
```

## API Development

### Adding New Endpoints

1. **Define the model** in `models.py`
2. **Add service functions** in `service.py`
3. **Create router handlers** in `router.py`
4. **Add tests** in `tests/`

Example:

```python
# models.py
class NewResource(NittySQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100)

# service.py
def create_new_resource(*, session: Session, name: str) -> NewResource:
    db_obj = NewResource(name=name)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

# router.py
@router.post("/", response_model=NewResource)
def create_resource(
    session: DbSession,
    name: str,
    current_user: Annotated[User, Depends(get_current_user)]
) -> Any:
    return service.create_new_resource(session=session, name=name)
```

### Error Handling

Use FastAPI's HTTPException for consistent error responses:

```python
from fastapi import HTTPException

# 404 Not Found
raise HTTPException(status_code=404, detail="Resource not found")

# 403 Forbidden
raise HTTPException(status_code=403, detail="Not enough permissions")

# 400 Bad Request
raise HTTPException(status_code=400, detail="Invalid input data")
```

### Validation

Use Pydantic models for request/response validation:

```python
from pydantic import Field, validator

class CreateResourceRequest(NittySQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

## Testing

### Test Structure

```python
# tests/test_new_feature.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_resource():
    response = client.post(
        "/api/v1/resources/",
        json={"name": "Test Resource"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Resource"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_user.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_create"
```

### Test Database

Use a separate test database:

```python
# tests/conftest.py
import pytest
from sqlmodel import Session, create_engine
from app.database import get_db
from app.main import app

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///./test.db")
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(test_db):
    def get_test_db():
        yield test_db

    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

## Authentication Development

### Adding New Auth Features

1. **Update models** in `auth/models.py`
2. **Add service functions** in `auth/service.py`
3. **Create endpoints** in `auth/router.py`

### JWT Token Development

```python
# Create custom token payload
class TokenPayload(NittySQLModel):
    sub: str | None = None
    exp: int | None = None
    iat: int | None = None

# Create token with custom claims
def create_access_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## Performance Optimization

### Database Queries

```python
# Use select() for better performance
from sqlmodel import select

# Good
statement = select(User).where(User.email == email)
user = session.exec(statement).first()

# Avoid
user = session.query(User).filter(User.email == email).first()
```

### Caching

```python
# Add caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_by_id(user_id: str) -> User:
    # Expensive database operation
    pass
```

### Pagination

```python
# Always implement pagination for list endpoints
def get_resources(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Resource]:
    statement = select(Resource).offset(skip).limit(limit)
    return session.exec(statement).all()
```

## Debugging

### Development Tools

```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)

def create_resource(data: dict):
    logger.info(f"Creating resource with data: {data}")
    # ... implementation
```

### Database Debugging

```python
# Enable SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or in development
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=True  # Log all SQL statements
)
```

### API Debugging

```bash
# Use curl for testing
curl -X POST "http://localhost:8000/api/v1/resources/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Resource"}'

# Use httpie (more user-friendly)
pip install httpie
http POST localhost:8000/api/v1/resources/ name="Test Resource"
```

## Git Workflow

### Branch Naming

- `feature/description`: New features
- `bugfix/description`: Bug fixes
- `hotfix/description`: Critical fixes
- `refactor/description`: Code refactoring

### Commit Messages

Follow conventional commits:

```bash
feat: add user registration endpoint
fix: resolve database connection issue
docs: update API documentation
test: add tests for event creation
refactor: simplify authentication logic
```

### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Run all checks (format, lint, test)
4. Create pull request
5. Code review
6. Merge to main

## Code Review Guidelines

### What to Look For

- **Functionality**: Does the code work as intended?
- **Security**: Are there any security vulnerabilities?
- **Performance**: Are there any performance issues?
- **Maintainability**: Is the code easy to understand and maintain?
- **Testing**: Are there adequate tests?

### Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No security vulnerabilities
- [ ] Proper error handling
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Proper logging
- [ ] Database migrations included

## Common Patterns

### Service Layer Pattern

```python
# service.py
def create_resource(*, session: Session, data: CreateResourceRequest) -> Resource:
    """Create a new resource with business logic."""
    # Validation
    if not data.name:
        raise ValueError("Name is required")

    # Business logic
    db_obj = Resource.model_validate(data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
```

### Repository Pattern

```python
# repositories/resource_repository.py
class ResourceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: CreateResourceRequest) -> Resource:
        db_obj = Resource.model_validate(data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get_by_id(self, resource_id: UUID) -> Resource | None:
        statement = select(Resource).where(Resource.id == resource_id)
        return self.session.exec(statement).first()
```

This development guide provides comprehensive information for contributing to the Nitty service, from setup to deployment.
