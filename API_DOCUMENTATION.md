# Tammy AI Assistant - API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API is open. In production, use JWT tokens:

```bash
Authorization: Bearer <your-token>
```

## Endpoints

### Chat

#### POST /api/chat

Chat with Tammy using natural language.

**Request:**
```json
{
  "message": "Schedule a meeting with John tomorrow at 2pm",
  "user_id": "user123",
  "context": {},
  "session_id": "session123"
}
```

**Response:**
```json
{
  "response": "I'll help you schedule that appointment...",
  "intent": "schedule_appointment",
  "entities": {
    "names": ["John"],
    "date": "2025-11-10",
    "time": "14:00"
  },
  "actions": [
    {
      "type": "schedule_appointment",
      "data": {...}
    }
  ],
  "confidence": 0.85,
  "suggestions": ["Check my calendar", "Find available time"],
  "timestamp": "2025-11-09T10:30:00"
}
```

#### GET /api/chat/capabilities

Get Tammy's capabilities.

**Response:**
```json
{
  "capabilities": [...],
  "examples": [...]
}
```

### Appointments

#### POST /api/appointments

Create a new appointment.

**Request:**
```json
{
  "user_id": "user123",
  "title": "Team Meeting",
  "description": "Weekly sync",
  "start_time": "2025-11-10T14:00:00",
  "duration_minutes": 60,
  "attendees": ["john@example.com"],
  "location": "Conference Room A"
}
```

**Response:** `201 Created`
```json
{
  "id": "appt-123",
  "user_id": "user123",
  "title": "Team Meeting",
  "start_time": "2025-11-10T14:00:00",
  "end_time": "2025-11-10T15:00:00",
  "status": "scheduled",
  ...
}
```

#### GET /api/appointments

Get appointments for a user.

**Query Parameters:**
- `user_id` (required): User ID
- `start_date` (optional): Filter start date (ISO format)
- `end_date` (optional): Filter end date (ISO format)

**Response:** `200 OK`
```json
[
  {
    "id": "appt-123",
    "title": "Team Meeting",
    ...
  }
]
```

#### GET /api/appointments/{appointment_id}

Get a specific appointment.

**Response:** `200 OK` or `404 Not Found`

#### PUT /api/appointments/{appointment_id}

Update an appointment.

**Request:**
```json
{
  "title": "Updated Meeting Title",
  "start_time": "2025-11-10T15:00:00"
}
```

**Response:** `200 OK` or `404 Not Found`

#### DELETE /api/appointments/{appointment_id}

Delete an appointment.

**Response:** `204 No Content` or `404 Not Found`

#### GET /api/appointments/user/{user_id}/upcoming

Get upcoming appointments.

**Query Parameters:**
- `hours` (optional, default: 24): Look ahead hours

**Response:** `200 OK`

#### POST /api/appointments/{appointment_id}/reschedule

Reschedule an appointment.

**Query Parameters:**
- `new_start_time` (required): New start time (ISO format)

**Response:** `200 OK` or `400 Bad Request`

### Tasks

#### POST /api/tasks

Create a new task.

**Request:**
```json
{
  "user_id": "user123",
  "title": "Review proposal",
  "description": "Review Q4 proposal",
  "priority": "high",
  "due_date": "2025-11-15T17:00:00",
  "project": "Q4 Planning"
}
```

**Response:** `201 Created`

#### GET /api/tasks

Get tasks for a user.

**Query Parameters:**
- `user_id` (required): User ID
- `status` (optional): Filter by status
- `priority` (optional): Filter by priority

**Response:** `200 OK`

#### GET /api/tasks/{task_id}

Get a specific task.

**Response:** `200 OK` or `404 Not Found`

#### PUT /api/tasks/{task_id}

Update a task.

**Response:** `200 OK` or `404 Not Found`

#### DELETE /api/tasks/{task_id}

Delete a task.

**Response:** `204 No Content` or `404 Not Found`

#### POST /api/tasks/{task_id}/complete

Mark a task as completed.

**Response:** `200 OK` or `404 Not Found`

#### GET /api/tasks/user/{user_id}/overdue

Get overdue tasks.

**Response:** `200 OK`

#### GET /api/tasks/user/{user_id}/today

Get tasks due today.

**Response:** `200 OK`

### Contacts

#### POST /api/contacts

Create a new contact.

**Request:**
```json
{
  "user_id": "user123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_number": "555-1234",
  "company": "Acme Corp",
  "job_title": "Manager"
}
```

**Response:** `201 Created`

#### GET /api/contacts

Get all contacts for a user.

**Query Parameters:**
- `user_id` (required): User ID

**Response:** `200 OK`

#### GET /api/contacts/search/

Search contacts.

**Query Parameters:**
- `user_id` (required): User ID
- `query` (required): Search query

**Response:** `200 OK`

#### GET /api/contacts/{contact_id}

Get a specific contact.

**Response:** `200 OK` or `404 Not Found`

#### PUT /api/contacts/{contact_id}

Update a contact.

**Response:** `200 OK` or `404 Not Found`

#### DELETE /api/contacts/{contact_id}

Delete a contact.

**Response:** `204 No Content` or `404 Not Found`

### Visitors

#### POST /api/visitors

Create a visitor record.

**Request:**
```json
{
  "full_name": "Jane Smith",
  "company": "Client Corp",
  "email": "jane@client.com",
  "host_name": "John Doe",
  "visit_type": "in_person",
  "purpose": "Product demo",
  "scheduled_time": "2025-11-09T14:00:00"
}
```

**Response:** `201 Created`

#### POST /api/visitors/{visitor_id}/check-in

Check in a visitor.

**Query Parameters:**
- `badge_number` (optional): Badge number

**Response:** `200 OK` or `404 Not Found`

#### POST /api/visitors/{visitor_id}/check-out

Check out a visitor.

**Response:** `200 OK` or `404 Not Found`

#### GET /api/visitors/current/all

Get all currently checked-in visitors.

**Response:** `200 OK`

#### GET /api/visitors/scheduled/upcoming

Get scheduled visitors.

**Query Parameters:**
- `hours` (optional, default: 24): Look ahead hours

**Response:** `200 OK`

### Messages

#### POST /api/messages

Create a message.

**Request:**
```json
{
  "message_type": "email",
  "direction": "inbound",
  "from_email": "sender@example.com",
  "to_email": "user@example.com",
  "subject": "Meeting request",
  "body": "Can we schedule a meeting?",
  "priority": "normal"
}
```

**Response:** `201 Created`

#### GET /api/messages

Get messages.

**Query Parameters:**
- `message_type` (optional): Filter by type
- `status` (optional): Filter by status
- `direction` (optional): Filter by direction

**Response:** `200 OK`

#### GET /api/messages/unread/all

Get unread messages.

**Response:** `200 OK`

#### POST /api/messages/{message_id}/read

Mark message as read.

**Response:** `200 OK` or `404 Not Found`

#### POST /api/messages/{message_id}/archive

Archive a message.

**Response:** `200 OK` or `404 Not Found`

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Default: 60 requests per minute per IP address.

## Interactive Documentation

Visit these URLs for interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
