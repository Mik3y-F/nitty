# Frequently Asked Questions

## General Questions

### What is Nitty?

Nitty is a FastAPI-based service for managing professional communities and their events. It provides a comprehensive platform for users to create communities, organize events, and connect with like-minded professionals.

### What technologies does Nitty use?

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLModel
- **Authentication**: JWT tokens
- **Migrations**: Alembic
- **Documentation**: OpenAPI/Swagger

### Is Nitty open source?

Yes, Nitty is open source and available under the MIT License.

## Installation & Setup

### What are the system requirements?

- Python 3.11 or higher
- PostgreSQL 12 or higher
- 2GB RAM minimum
- 1GB disk space

### How do I install Nitty?

See our [Quick Start Guide](QUICKSTART.md) for step-by-step installation instructions.

### Can I run Nitty without Docker?

Yes, you can run Nitty without Docker. You'll need to install PostgreSQL locally and configure the database connection in your `.env` file.

### What's the difference between development and production setup?

Development setup is optimized for local development with hot reloading and debug logging. Production setup includes security hardening, performance optimization, and proper deployment configurations.

## Database

### How do I backup my database?

```bash
# Create backup
docker-compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup.sql

# Restore backup
docker-compose exec -T db psql -U ${POSTGRES_USER} ${POSTGRES_DB} < backup.sql
```

### How do I reset the database?

```bash
# Stop containers and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d
alembic upgrade head
```

### Can I use a different database?

Currently, Nitty is designed for PostgreSQL. Support for other databases may be added in future versions.

### How do I run database migrations?

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "Description"

# Rollback last migration
alembic downgrade -1
```

## Authentication

### How does authentication work?

Nitty uses JWT (JSON Web Tokens) for authentication. Users log in with email/password and receive a token that must be included in subsequent requests.

### How long do tokens last?

By default, tokens expire after 8 days (10080 minutes). This can be configured in the `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable.

### How do I get a token?

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password"
```

### Can I refresh tokens?

Currently, tokens cannot be refreshed. Users must log in again when their token expires.

### How do I change a user's password?

Password changes are not currently implemented in the API. This feature will be added in a future version.

## API Usage

### How do I use the API?

1. Register a user account
2. Login to get an access token
3. Include the token in the Authorization header: `Bearer <token>`
4. Make API requests

### What's the base URL for the API?

The API base URL is `/api/v1`. For local development: `http://localhost:8000/api/v1`

### How do I handle pagination?

Most list endpoints support `skip` and `limit` parameters:

```bash
curl "http://localhost:8000/api/v1/events/?skip=20&limit=10"
```

### How do I search for content?

Use the search endpoints:

```bash
# Search communities
curl "http://localhost:8000/api/v1/communities/search?q=python"

# Search events
curl "http://localhost:8000/api/v1/events/search?q=workshop"
```

### What's the difference between soft delete and permanent delete?

- **Soft delete**: Sets `is_active=False` but keeps the record in the database
- **Permanent delete**: Completely removes the record from the database

## Communities

### Who can create communities?

Any authenticated user can create communities.

### Who can create events in a community?

Only the creator of the community can create events in that community.

### Can I make a community private?

Yes, set `is_public=False` when creating or updating a community.

### How do I find communities I created?

Use the `/communities/my` endpoint (requires authentication).

## Events

### What timezone are event times in?

Event times are stored in UTC. Convert to local timezone when displaying to users.

### Can I create events without an end time?

Yes, `end_time` is optional. If not provided, the event will only have a start time.

### How do I find upcoming events?

Use the `/events/upcoming` endpoint.

### Can I create online events?

Yes, set `is_online=True` when creating an event. You can also specify a location for online events (e.g., "Zoom Meeting").

### How do I find events in a specific date range?

Use the `/events/date-range` endpoint with `start_date` and `end_date` parameters.

## Development

### How do I contribute to Nitty?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See our [Development Guide](DEVELOPMENT.md) for detailed instructions.

### How do I run tests?

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_user.py
```

### How do I add new features?

1. Create models in the appropriate module
2. Add service functions for business logic
3. Create router endpoints
4. Add tests
5. Update documentation

### What's the coding style?

We use Black for formatting, isort for import sorting, and flake8 for linting. See the [Development Guide](DEVELOPMENT.md) for details.

## Deployment

### How do I deploy to production?

See our [Deployment Guide](DEPLOYMENT.md) for comprehensive deployment instructions.

### Can I use Docker for production?

Yes, Docker is recommended for production deployment. Use the production Docker Compose configuration.

### How do I set up SSL/HTTPS?

Use a reverse proxy like nginx with SSL certificates. See the deployment guide for nginx configuration.

### How do I monitor the application?

- Use the `/health` endpoint for health checks
- Set up log aggregation
- Monitor database performance
- Use application metrics

## Troubleshooting

### The server won't start

1. Check if the port is already in use: `lsof -i :8000`
2. Verify database connection
3. Check environment variables
4. View logs for error messages

### Database connection errors

1. Ensure PostgreSQL is running
2. Check database credentials in `.env`
3. Verify database exists
4. Check network connectivity

### Authentication not working

1. Verify token is included in Authorization header
2. Check token hasn't expired
3. Ensure user account is active
4. Verify token format: `Bearer <token>`

### API returns 404 errors

1. Check the endpoint URL is correct
2. Verify the API version (`/api/v1`)
3. Ensure the resource exists
4. Check authentication if required

### Migration errors

1. Check current migration status: `alembic current`
2. Verify database schema matches migrations
3. Try rolling back and reapplying: `alembic downgrade -1 && alembic upgrade head`
4. Check for conflicting migrations

## Performance

### How can I improve performance?

1. Add database indexes for frequently queried fields
2. Use connection pooling
3. Implement caching for expensive operations
4. Optimize database queries
5. Use pagination for large datasets

### How many users can Nitty handle?

Performance depends on your hardware and configuration. With proper setup, Nitty can handle thousands of concurrent users.

### Should I use a CDN?

For production deployments with many users, a CDN can help with static file delivery and reduce server load.

## Security

### How secure is Nitty?

Nitty implements industry-standard security practices:

- JWT authentication
- Password hashing with bcrypt
- SQL injection protection via SQLModel
- Input validation with Pydantic
- CORS configuration

### How do I secure my deployment?

1. Use strong passwords and secrets
2. Enable HTTPS/SSL
3. Configure firewall rules
4. Keep dependencies updated
5. Use environment variables for secrets
6. Implement rate limiting
7. Set up monitoring and alerting

### Can I add custom authentication?

Yes, you can extend the authentication system by modifying the `deps.py` file and adding custom authentication logic.

## Support

### Where can I get help?

- Check this FAQ
- Read the documentation
- Open an issue on GitHub
- Join community discussions

### How do I report bugs?

1. Check if the issue is already reported
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs if applicable

### How do I request features?

1. Check if the feature is already requested
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Implementation suggestions if any

### Is there a roadmap?

Check the GitHub repository for the latest roadmap and planned features.

## License

### What license does Nitty use?

Nitty is licensed under the MIT License. See the LICENSE file for details.

### Can I use Nitty commercially?

Yes, the MIT License allows commercial use.

### Do I need to attribute Nitty?

While not required, attribution is appreciated. You can include a link to the Nitty repository in your project.

---

Still have questions? Feel free to open an issue on GitHub or join our community discussions!
