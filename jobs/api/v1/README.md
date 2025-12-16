# API v1 Documentation

REST API v1 for Job Search application.

## Base URL

```
/api/v1/
```

## Authentication

The API uses **Session Authentication** (for web browsers) and **Basic Authentication** (for programmatic access).

**Basic Auth:**
```
Authorization: Basic base64(username:password)
```

## Endpoints Overview

| Resource | Endpoint | Methods | Description |
|----------|----------|---------|-------------|
| Jobs | `/jobs/` | GET, POST | List/create job entries |
| Job | `/jobs/{id}/` | GET, PUT, PATCH, DELETE | Job details/update/delete |
| Resume Statuses | `/resume-status/` | GET, POST, PUT, PATCH, DELETE | Resume submission status tracking |
| Categories | `/categories/` | GET | List categories (read-only) |
| Tags | `/tags/` | GET | List tags (read-only) |
| Templates | `/templates/` | GET, POST, PUT, PATCH, DELETE | Job templates |
| Attachments | `/attachments/` | GET, POST, DELETE | File attachments |
| Notifications | `/notifications/` | GET, POST, PUT, PATCH, DELETE | User notifications |
| History | `/history/` | GET | Job change history (read-only) |
| Profile | `/profile/` | GET, PUT, PATCH | User profile settings |
| Statistics | `/statistics/` | GET | Comprehensive job statistics |
| Monthly Report | `/monthly-report/` | GET | Monthly report with submitted documents |
| Calendar | `/calendar/` | GET | Calendar events (interviews, deadlines) |

## Jobs

**List/Filter:**
```
GET /api/v1/jobs/?search=python&status=applied&priority=high&ordering=-created_at
```

**Query parameters:** `search`, `status`, `priority`, `work_type`, `source`, `category`, `tag`, `ordering`, `page`

**Create:**
```json
POST /api/v1/jobs/
{
  "job_title": "Python Developer",
  "employer": "Tech Company",
  "job_url": "https://example.com/job",
  "category_id": 1,
  "tag_ids": [1, 2],
  "priority": "high"
}
```

**Actions:**
- `GET /api/v1/jobs/{id}/history/` - Get job history
- `GET /api/v1/jobs/{id}/attachments/` - Get job attachments
- `GET /api/v1/jobs/{id}/resume_statuses/` - Get resume statuses
- `POST /api/v1/jobs/{id}/resume_statuses/` - Add resume status

## Resume Submission Statuses

**Status types:**
- `resume_sent` - Resume Sent
- `confirmation_received` - Confirmation Received
- `interview_scheduled` - Interview Scheduled
- `interview_passed` - Interview Passed
- `another_interview_scheduled` - Another Interview Scheduled
- `documents_requested` - Documents Requested
- `rejection_received` - Rejection Received

**Create:**
```json
POST /api/v1/resume-status/
{
  "job_entry_id": 1,
  "status_type": "resume_sent",
  "date_time": "2025-11-15T10:00:00Z",
  "notes": "Sent via email"
}
```

## Statistics & Reports

**Statistics:**
```
GET /api/v1/statistics/
```
Returns: total counts, status distribution, success/rejection rates, time-based stats, top employers, salary stats, upcoming events.

**Monthly Report:**
```
GET /api/v1/monthly-report/?month=2025-11
```
Returns job entries with submitted documents for the specified month.

**Calendar:**
```
GET /api/v1/calendar/?start=2025-11-01T00:00:00Z&end=2025-11-30T23:59:59Z
```
Returns calendar events (interviews, follow-ups, deadlines).

## Notifications

**Actions:**
- `POST /api/v1/notifications/{id}/mark_read/` - Mark as read
- `POST /api/v1/notifications/mark_all_read/` - Mark all as read
- `GET /api/v1/notifications/unread_count/` - Get unread count

**Filters:** `is_read`, `notification_type`

## Pagination

All list endpoints use pagination (default: 20 items per page).

**Response:**
```json
{
  "count": 100,
  "next": "http://example.com/api/v1/jobs/?page=2",
  "previous": null,
  "results": [...]
}
```

## Response Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Resource deleted
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Usage Examples

### Python (requests)

```python
import requests

BASE_URL = 'http://localhost:8000/api/v1'
session = requests.Session()
session.auth = ('username', 'password')

# List jobs
jobs = session.get(f'{BASE_URL}/jobs/').json()

# Create job
new_job = {'job_title': 'Python Developer', 'employer': 'Tech Co', 'job_url': 'https://example.com/job'}
created = session.post(f'{BASE_URL}/jobs/', json=new_job).json()

# Update job
session.patch(f'{BASE_URL}/jobs/{job_id}/', json={'status': 'applied'})
```

### cURL

```bash
# List jobs
curl -u user:pass http://localhost:8000/api/v1/jobs/

# Create job
curl -u user:pass -X POST http://localhost:8000/api/v1/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"job_title": "Python Developer", "employer": "Tech Co", "job_url": "https://example.com/job"}'
```

## Browsable API

Django REST Framework provides a browsable API interface:
```
http://localhost:8000/api/v1/jobs/
```
