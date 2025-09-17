# Quick Start Guide

Get up and running with Nitty in 5 minutes!

## Prerequisites

- Python 3.11+
- PostgreSQL 12+
- UV package manager

## 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd nitty

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env
```

## 2. Database Setup

### Option A: Using Docker (Recommended)

```bash
# Start PostgreSQL
docker run --name nitty-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=nitty_dev \
  -p 5432:5432 \
  -d postgres:15

# Update .env file
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=nitty_dev
```

### Option B: Local PostgreSQL

```bash
# Create database
createdb nitty_dev

# Update .env file with your credentials
POSTGRES_SERVER=localhost
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=nitty_dev
```

## 3. Run Migrations

```bash
# Apply database migrations
alembic upgrade head
```

## 4. Start the Server

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Test the API

Open your browser and go to:

- **API Documentation**: <http://localhost:8000/docs>
- **Alternative Docs**: <http://localhost:8000/redoc>

## 6. Create Your First User

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User"
  }'
```

## 7. Login and Get Token

```bash
# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

Save the `access_token` from the response.

## 8. Create Your First Community

```bash
# Create a community (replace <token> with your actual token)
curl -X POST "http://localhost:8000/api/v1/communities/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Developers",
    "description": "A community for Python enthusiasts",
    "is_public": true
  }'
```

Save the `id` from the community response.

## 9. Create Your First Event

```bash
# Create an event (replace <token> and <community_id>)
curl -X POST "http://localhost:8000/api/v1/events/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Workshop",
    "description": "Learn Python basics",
    "start_time": "2024-02-01T10:00:00Z",
    "end_time": "2024-02-01T12:00:00Z",
    "location": "Conference Room A",
    "community_id": "<community_id>",
    "max_attendees": 50
  }'
```

## 10. Explore the API

### List Communities

```bash
curl "http://localhost:8000/api/v1/communities/"
```

### List Events

```bash
curl "http://localhost:8000/api/v1/events/"
```

### Search Events

```bash
curl "http://localhost:8000/api/v1/events/search?q=python"
```

### Get Upcoming Events

```bash
curl "http://localhost:8000/api/v1/events/upcoming"
```

## Using the Interactive API Docs

1. Go to <http://localhost:8000/docs>
2. Click "Authorize" button
3. Enter your token: `Bearer <your-token>`
4. Click "Authorize"
5. Now you can test all endpoints directly in the browser!

## Common Commands

```bash
# View logs
tail -f app.log

# Run tests
pytest

# Format code
black app/

# Check code quality
flake8 app/

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database connection
psql -h localhost -U postgres -d nitty_dev

# View database logs
docker logs nitty-postgres
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Migration Issues

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

## Next Steps

- Read the [API Documentation](API.md) for detailed endpoint information
- Check out the [Development Guide](DEVELOPMENT.md) for contributing
- See [Deployment Guide](DEPLOYMENT.md) for production setup

## Need Help?

- Check the [FAQ](FAQ.md) for common questions
- Open an issue on GitHub
- Join our community discussions

Happy coding! 🚀
