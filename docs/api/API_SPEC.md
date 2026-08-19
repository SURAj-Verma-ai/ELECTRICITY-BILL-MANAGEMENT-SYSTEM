# EBMS API Specification

## API Overview

Base URL: `https://api.ebms.local/api/v1`

All endpoints require authentication via JWT token in the `Authorization` header.

## Authentication

### Getting a Token
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response (200 OK):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### Using Token
```http
GET /bills
Authorization: Bearer <access_token>
```

## API Endpoints

### Bills Management

#### List Bills
```http
GET /bills
Query Parameters:
  - page: int (default: 1)
  - limit: int (default: 20, max: 100)
  - status: string (pending|paid|overdue)
  - sort: string (date|amount|status)

Response (200 OK):
{
  "data": [
    {
      "id": "bill_123",
      "user_id": "user_456",
      "amount": 1500.50,
      "due_date": "2024-01-15",
      "status": "pending",
      "created_at": "2024-01-05T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

#### Get Bill Details
```http
GET /bills/{bill_id}

Response (200 OK):
{
  "id": "bill_123",
  "user_id": "user_456",
  "amount": 1500.50,
  "due_date": "2024-01-15",
  "status": "pending",
  "usage": {
    "kwh": 5000,
    "unit_rate": 0.30,
    "taxes": 150.50,
    "discount": 0
  },
  "created_at": "2024-01-05T10:30:00Z",
  "updated_at": "2024-01-05T10:30:00Z"
}
```

#### Create Bill
```http
POST /bills
Content-Type: application/json

{
  "user_id": "user_456",
  "usage_kwh": 5000,
  "billing_period": "2024-01",
  "notes": "Winter billing"
}

Response (201 Created):
{
  "id": "bill_789",
  "user_id": "user_456",
  "amount": 1500.50,
  "status": "pending",
  "created_at": "2024-01-05T10:30:00Z"
}
```

### Payments

#### Record Payment
```http
POST /bills/{bill_id}/payments
Content-Type: application/json

{
  "amount": 1500.50,
  "method": "credit_card|bank_transfer|cash",
  "reference": "TXN_123456"
}

Response (201 Created):
{
  "id": "payment_123",
  "bill_id": "bill_123",
  "amount": 1500.50,
  "method": "credit_card",
  "status": "completed",
  "created_at": "2024-01-06T14:20:00Z"
}
```

### Users

#### Get User Profile
```http
GET /users/me

Response (200 OK):
{
  "id": "user_456",
  "email": "user@example.com",
  "name": "John Doe",
  "account_type": "residential",
  "status": "active",
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### Update Profile
```http
PUT /users/me
Content-Type: application/json

{
  "name": "Jane Doe",
  "phone": "+1234567890",
  "address": "123 Main St"
}

Response (200 OK):
{
  "id": "user_456",
  "email": "user@example.com",
  "name": "Jane Doe",
  "phone": "+1234567890",
  "address": "123 Main St"
}
```

### Reports

#### Generate Bill Report
```http
POST /reports/bills
Content-Type: application/json

{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "format": "pdf|csv|json"
}

Response (202 Accepted):
{
  "report_id": "report_123",
  "status": "processing",
  "estimated_time": 5,
  "download_url": "/reports/report_123/download"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {
    "amount": "Must be a positive number"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Missing or invalid authentication token"
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "message": "You do not have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "error_id": "err_123456"
}
```

## Rate Limiting

- **Free Tier**: 100 requests/hour
- **Premium Tier**: 10,000 requests/hour
- **Enterprise**: Custom limits

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704067200
```

## Webhook Events

Subscribe to events via `/webhooks` endpoints:

- `bill.created`
- `bill.paid`
- `bill.overdue`
- `payment.received`
- `user.registered`

Example webhook payload:
```json
{
  "event": "bill.paid",
  "timestamp": "2024-01-06T14:20:00Z",
  "data": {
    "bill_id": "bill_123",
    "user_id": "user_456",
    "amount": 1500.50
  }
}
```

## Versioning

API uses URL versioning: `/api/v1`, `/api/v2`, etc.

Deprecation warnings in response headers:
```
Deprecation: true
Sunset: Sun, 01 Jan 2025 00:00:00 GMT
```
