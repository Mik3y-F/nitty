# Deployment Guide

This guide covers different deployment options for the Nitty service.

## Prerequisites

- Docker and Docker Compose
- PostgreSQL database
- Domain name (for production)
- SSL certificate (for production)

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Application
SECRET_KEY=your-secret-key-here
API_V1_STR=/api/v1
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ENVIRONMENT=production

# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=nitty_user
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=nitty_db

# Email (optional)
EMAIL_TEST_USER=test@example.com
```

## Docker Deployment

### 1. Build the Image

```bash
docker build -t nitty:latest .
```

### 2. Run with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

### 3. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - POSTGRES_SERVER=db
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - ENVIRONMENT=production
    depends_on:
      - db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

## Database Setup

### 1. Run Migrations

```bash
# Using Docker
docker-compose exec web alembic upgrade head

# Or locally
alembic upgrade head
```

### 2. Create Initial Data (Optional)

```bash
# Create a superuser
docker-compose exec web python -c "
from app.database import get_db
from app.auth.service import create_user
from app.auth.models import UserCreate
from sqlmodel import Session

session = next(get_db())
user_create = UserCreate(
    email='admin@example.com',
    password='admin123',
    full_name='Admin User',
    is_superuser=True
)
create_user(session=session, user_create=user_create)
"
```

## Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Production Checklist

### Security

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable CORS properly
- [ ] Use environment-specific settings

### Performance

- [ ] Configure database connection pooling
- [ ] Set up Redis for caching (optional)
- [ ] Enable gzip compression
- [ ] Configure static file serving
- [ ] Set up monitoring and logging

### Monitoring

- [ ] Set up health checks
- [ ] Configure log aggregation
- [ ] Set up error tracking
- [ ] Monitor database performance
- [ ] Set up backup procedures

## Health Checks

The application provides health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup.sql

# Restore backup
docker-compose exec -T db psql -U ${POSTGRES_USER} ${POSTGRES_DB} < backup.sql
```

### Automated Backups

Create a backup script:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.sql"

docker-compose exec -T db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > ${BACKUP_FILE}

# Upload to cloud storage (optional)
# aws s3 cp ${BACKUP_FILE} s3://your-backup-bucket/

# Clean up old backups (keep last 7 days)
find . -name "backup_*.sql" -mtime +7 -delete
```

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple App Instances**: Run multiple web containers
3. **Database**: Consider read replicas for read-heavy workloads

### Vertical Scaling

1. **Increase Resources**: More CPU/memory for containers
2. **Database Optimization**: Tune PostgreSQL settings
3. **Caching**: Add Redis for session storage and caching

## Troubleshooting

### Common Issues

1. **Database Connection Errors**

   ```bash
   # Check database status
   docker-compose exec db pg_isready -U ${POSTGRES_USER}

   # View database logs
   docker-compose logs db
   ```

2. **Application Errors**

   ```bash
   # View application logs
   docker-compose logs web

   # Check application health
   curl http://localhost:8000/health
   ```

3. **Migration Issues**

   ```bash
   # Check migration status
   docker-compose exec web alembic current

   # Rollback migration
   docker-compose exec web alembic downgrade -1
   ```

### Log Analysis

```bash
# View real-time logs
docker-compose logs -f web

# Filter error logs
docker-compose logs web | grep ERROR

# View specific time range
docker-compose logs --since="2024-01-01T00:00:00" web
```

## Security Considerations

### Production Security

1. **Secrets Management**
   - Use environment variables or secret management services
   - Never commit secrets to version control
   - Rotate secrets regularly

2. **Network Security**
   - Use private networks for database access
   - Implement proper firewall rules
   - Use VPN for administrative access

3. **Application Security**
   - Keep dependencies updated
   - Use security headers
   - Implement proper CORS policies
   - Regular security audits

### SSL/TLS Setup

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Use Let's Encrypt (production)
certbot --nginx -d your-domain.com
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_community_id ON events(community_id);
CREATE INDEX idx_communities_created_by ON communities(created_by);
```

### Application Optimization

1. **Connection Pooling**

   ```python
   # In database.py
   engine = create_engine(
       str(settings.SQLALCHEMY_DATABASE_URI),
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True
   )
   ```

2. **Caching**

   ```python
   # Add Redis caching for frequently accessed data
   from redis import Redis

   redis_client = Redis(host='redis', port=6379, db=0)
   ```

## Monitoring and Alerting

### Application Metrics

```python
# Add metrics endpoint
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration

```python
# In main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

This deployment guide provides comprehensive instructions for deploying the Nitty service in various environments, from development to production.
