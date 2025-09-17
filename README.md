# Nitty - Professional Communities but Fun

Nitty is a FastAPI-based service for managing professional communities and their events. It provides a comprehensive platform for users to create communities, organize events, and connect with like-minded professionals.

## Features

### 🔐 Authentication & Authorization

- JWT-based authentication
- User registration and login
- Role-based access control
- Secure password hashing with bcrypt

### 👥 Community Management

- Create and manage professional communities
- Public and private community support
- Community search and filtering
- User ownership and permissions

### 📅 Event Management

- Create and manage community events
- Event scheduling with start/end times
- Location support (physical and online)
- Attendee limits and public/private events
- Event search and filtering
- Date range queries

### 🔍 Advanced Features

- Full-text search across communities and events
- Pagination for all list endpoints
- Soft delete functionality
- Comprehensive logging
- RESTful API design

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLModel
- **Authentication**: JWT tokens
- **Migrations**: Alembic
- **Password Hashing**: bcrypt
- **Validation**: Pydantic
- **Documentation**: OpenAPI/Swagger

## Project Structure

```bash
app/
├── auth/                    # Authentication module
│   ├── models.py           # User models and schemas
│   ├── router.py           # Auth endpoints
│   └── service.py          # Auth business logic
├── communities/            # Community management
│   ├── models.py           # Community models
│   ├── router.py           # Community endpoints
│   └── service.py          # Community business logic
├── events/                 # Event management
│   ├── models.py           # Event models
│   ├── router.py           # Event endpoints
│   └── service.py          # Event business logic
├── config.py               # Application configuration
├── database.py             # Database connection
├── deps.py                 # Dependencies (auth, etc.)
└── main.py                 # FastAPI application
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- UV package manager

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd nitty
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run database migrations**

   ```bash
   alembic upgrade head
   ```

5. **Start the development server**

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: <http://localhost:8000/docs>
- **ReDoc documentation**: <http://localhost:8000/redoc>
- **OpenAPI schema**: <http://localhost:8000/openapi.json>

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/login/access-token` | Login and get access token | No |
| POST | `/signup` | Register new user | No |

### Communities (`/api/v1/communities`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create new community | Yes |
| GET | `/` | List communities | No |
| GET | `/search` | Search communities | No |
| GET | `/my` | Get user's communities | Yes |
| GET | `/{id}` | Get specific community | No |
| PUT | `/{id}` | Update community | Yes (creator only) |
| DELETE | `/{id}` | Delete community | Yes (creator only) |
| DELETE | `/{id}/permanent` | Permanently delete | Yes (creator only) |

### Events (`/api/v1/events`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create new event | Yes |
| GET | `/` | List events | No |
| GET | `/search` | Search events | No |
| GET | `/upcoming` | Get upcoming events | No |
| GET | `/my` | Get user's events | Yes |
| GET | `/community/{id}` | Get community events | No |
| GET | `/date-range` | Get events by date range | No |
| GET | `/{id}` | Get specific event | No |
| PUT | `/{id}` | Update event | Yes (creator only) |
| DELETE | `/{id}` | Delete event | Yes (creator only) |
| DELETE | `/{id}/permanent` | Permanently delete | Yes (creator only) |

## Data Models

### User

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Community

```json
{
  "id": "uuid",
  "name": "Python Developers",
  "description": "A community for Python enthusiasts",
  "is_public": true,
  "is_active": true,
  "created_by": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Event

```json
{
  "id": "uuid",
  "title": "Python Workshop",
  "description": "Learn Python basics",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T12:00:00Z",
  "location": "Conference Room A",
  "is_online": false,
  "max_attendees": 50,
  "is_public": true,
  "is_active": true,
  "community_id": "uuid",
  "created_by": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

1. **Register a new user**:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/signup" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "user@example.com",
          "password": "securepassword",
          "full_name": "John Doe"
        }'
   ```

2. **Login to get a token**:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=user@example.com&password=securepassword"
   ```

## Usage Examples

### Create a Community

```bash
curl -X POST "http://localhost:8000/api/v1/communities/" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "AI Enthusiasts",
       "description": "Discussing AI and machine learning",
       "is_public": true
     }'
```

### Create an Event

```bash
curl -X POST "http://localhost:8000/api/v1/events/" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "AI Workshop",
       "description": "Introduction to machine learning",
       "start_time": "2024-02-01T10:00:00Z",
       "end_time": "2024-02-01T12:00:00Z",
       "location": "Tech Hub",
       "community_id": "<community-uuid>",
       "max_attendees": 30
     }'
```

### Search Events

```bash
curl "http://localhost:8000/api/v1/events/search?q=workshop&limit=10"
```

### Get Upcoming Events

```bash
curl "http://localhost:8000/api/v1/events/upcoming?limit=20"
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_user.py
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Configuration

The application uses environment variables for configuration. Key settings:

- `SECRET_KEY`: JWT secret key
- `POSTGRES_SERVER`: Database host
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## Deployment

### Docker

```bash
# Build image
docker build -t nitty .

# Run container
docker run -p 8000:8000 nitty
```

### Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support, please open an issue in the repository or contact the development team.
