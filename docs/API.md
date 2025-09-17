# Nitty API Documentation

## Overview

The Nitty API provides endpoints for managing users, communities, and events. All endpoints are prefixed with `/api/v1`.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

## Base URL

```bash
http://localhost:8000/api/v1
```

## Authentication Endpoints

### POST /auth/login/access-token

Login and get an access token.

**Request Body:**

```bash
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

**Status Codes:**

- `200`: Success
- `400`: Invalid credentials or inactive user

### POST /auth/signup

Register a new user.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false
}
```

**Status Codes:**

- `200`: Success
- `400`: User already exists

## Community Endpoints

### POST /communities/

Create a new community.

**Authentication:** Required

**Request Body:**

```json
{
  "name": "Python Developers",
  "description": "A community for Python enthusiasts",
  "is_public": true
}
```

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Python Developers",
  "description": "A community for Python enthusiasts",
  "is_public": true,
  "is_active": true,
  "created_by": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**

- `200`: Success
- `401`: Unauthorized

### GET /communities/

List communities with optional filtering.

**Query Parameters:**

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)
- `is_public` (bool, optional): Filter by public/private status
- `is_active` (bool, optional): Filter by active status

**Response:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Python Developers",
    "description": "A community for Python enthusiasts",
    "is_public": true,
    "is_active": true,
    "created_by": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET /communities/search

Search communities by name or description.

**Query Parameters:**

- `q` (string, required): Search query (1-100 characters)
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response:** Same as GET /communities/

### GET /communities/my

Get communities created by the current user.

**Authentication:** Required

**Query Parameters:**

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response:** Same as GET /communities/

### GET /communities/{community_id}

Get a specific community by ID.

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Python Developers",
  "description": "A community for Python enthusiasts",
  "is_public": true,
  "is_active": true,
  "created_by": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**

- `200`: Success
- `404`: Community not found

### PUT /communities/{community_id}

Update a community.

**Authentication:** Required (creator only)

**Request Body:**

```json
{
  "name": "Updated Community Name",
  "description": "Updated description",
  "is_public": false
}
```

**Response:** Same as GET /communities/{community_id}

**Status Codes:**

- `200`: Success
- `401`: Unauthorized
- `403`: Not enough permissions
- `404`: Community not found

### DELETE /communities/{community_id}

Delete a community (soft delete).

**Authentication:** Required (creator only)

**Response:**

```json
{
  "message": "Community deleted successfully"
}
```

**Status Codes:**

- `200`: Success
- `401`: Unauthorized
- `403`: Not enough permissions
- `404`: Community not found

### DELETE /communities/{community_id}/permanent

Permanently delete a community from the database.

**Authentication:** Required (creator only)

**Response:**

```json
{
  "message": "Community permanently deleted"
}
```

## Event Endpoints

### POST /events/

Create a new event.

**Authentication:** Required (community creator only)

**Request Body:**

```json
{
  "title": "Python Workshop",
  "description": "Learn Python basics",
  "start_time": "2024-02-01T10:00:00Z",
  "end_time": "2024-02-01T12:00:00Z",
  "location": "Conference Room A",
  "is_online": false,
  "max_attendees": 50,
  "is_public": true,
  "community_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "title": "Python Workshop",
  "description": "Learn Python basics",
  "start_time": "2024-02-01T10:00:00Z",
  "end_time": "2024-02-01T12:00:00Z",
  "location": "Conference Room A",
  "is_online": false,
  "max_attendees": 50,
  "is_public": true,
  "is_active": true,
  "community_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_by": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**

- `200`: Success
- `401`: Unauthorized
- `403`: Not enough permissions
- `404`: Community not found

### GET /events/

List events with optional filtering.

**Query Parameters:**

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)
- `community_id` (uuid, optional): Filter by community ID
- `is_public` (bool, optional): Filter by public/private status
- `is_active` (bool, optional): Filter by active status
- `upcoming_only` (bool, optional): Show only upcoming events (default: false)

**Response:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174002",
    "title": "Python Workshop",
    "description": "Learn Python basics",
    "start_time": "2024-02-01T10:00:00Z",
    "end_time": "2024-02-01T12:00:00Z",
    "location": "Conference Room A",
    "is_online": false,
    "max_attendees": 50,
    "is_public": true,
    "is_active": true,
    "community_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_by": "123e4567-e89b-12d3-a456-426614174001",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### GET /events/search

Search events by title, description, or location.

**Query Parameters:**

- `q` (string, required): Search query (1-100 characters)
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response:** Same as GET /events/

### GET /events/upcoming

Get upcoming events (start_time >= now).

**Query Parameters:**

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response:** Same as GET /events/

### GET /events/my

Get events created by the current user.

**Authentication:** Required

**Query Parameters:**

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response:** Same as GET /events/

### GET /events/community/{community_id}

Get events for a specific community.

**Query Parameters:**

- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response:** Same as GET /events/

**Status Codes:**

- `200`: Success
- `404`: Community not found

### GET /events/date-range

Get events within a specific date range.

**Query Parameters:**

- `start_date` (datetime, required): Start date (ISO format)
- `end_date` (datetime, required): End date (ISO format)
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100, max: 1000)

**Response:** Same as GET /events/

**Status Codes:**

- `200`: Success
- `400`: Start date must be before end date

### GET /events/{event_id}

Get a specific event by ID.

**Response:** Same as POST /events/ response

**Status Codes:**

- `200`: Success
- `404`: Event not found

### PUT /events/{event_id}

Update an event.

**Authentication:** Required (creator only)

**Request Body:**

```json
{
  "title": "Updated Event Title",
  "description": "Updated description",
  "max_attendees": 100
}
```

**Response:** Same as GET /events/{event_id}

**Status Codes:**

- `200`: Success
- `401`: Unauthorized
- `403`: Not enough permissions
- `404`: Event not found

### DELETE /events/{event_id}

Delete an event (soft delete).

**Authentication:** Required (creator only)

**Response:**

```json
{
  "message": "Event deleted successfully"
}
```

**Status Codes:**

- `200`: Success
- `401`: Unauthorized
- `403`: Not enough permissions
- `404`: Event not found

### DELETE /events/{event_id}/permanent

Permanently delete an event from the database.

**Authentication:** Required (creator only)

**Response:**

```json
{
  "message": "Event permanently deleted"
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Status Codes

- `200`: Success
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource doesn't exist
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server error

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in future versions.

## Pagination

All list endpoints support pagination using `skip` and `limit` parameters:

- `skip`: Number of records to skip (0-based)
- `limit`: Maximum number of records to return (max: 1000)

Example:

```bash
GET /api/v1/events/?skip=20&limit=10
```

## Filtering

Many endpoints support filtering through query parameters:

- Boolean filters: `is_public`, `is_active`, `upcoming_only`
- UUID filters: `community_id`
- Date filters: `start_date`, `end_date`

## Search

Search endpoints use case-insensitive partial matching:

- Communities: Searches name and description
- Events: Searches title, description, and location

## Data Types

- **UUID**: Universally unique identifier (string format)
- **DateTime**: ISO 8601 format (e.g., "2024-01-01T10:00:00Z")
- **Boolean**: true/false
- **Integer**: Whole numbers
- **String**: Text with length limits as specified

## Examples

### Complete Workflow

1. **Register a user:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/signup" \
        -H "Content-Type: application/json" \
        -d '{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}'
   ```

2. **Login to get token:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login/access-token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=user@example.com&password=password123"
   ```

3. **Create a community:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/communities/" \
        -H "Authorization: Bearer <token>" \
        -H "Content-Type: application/json" \
        -d '{"name": "Python Devs", "description": "Python community", "is_public": true}'
   ```

4. **Create an event:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/events/" \
        -H "Authorization: Bearer <token>" \
        -H "Content-Type: application/json" \
        -d '{"title": "Python Workshop", "start_time": "2024-02-01T10:00:00Z", "community_id": "<community-uuid>"}'
   ```

5. **Search for events:**

   ```bash
   curl "http://localhost:8000/api/v1/events/search?q=python"
   ```
