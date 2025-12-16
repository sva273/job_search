# Job Search System

🚀 **Smart job application tracker** - Organize, track, and manage your job search journey with ease. Stay on top of applications, interviews, and deadlines all in one place.

[![GitHub stars](https://img.shields.io/github/stars/sva273/job_search.svg?style=social&label=Star)](https://github.com/sva273/job_search)
[![GitHub forks](https://img.shields.io/github/forks/sva273/job_search.svg?style=social&label=Fork)](https://github.com/sva273/job_search/fork)

> ⭐ **If you find this project useful, please consider giving it a star on GitHub!** ⭐

## Features

- ✅ User registration and authentication
- ✅ Create and manage job entries (manual data entry)
- ✅ Track application process with detailed resume submission status history
- ✅ Multiple status tracking: Resume Sent, Confirmation Received, Interview Scheduled, Interview Passed, Another Interview Scheduled, Additional Documents Requested, Rejection Received
- ✅ Generate PDF documents with job information
- ✅ Job statistics with PDF export
- ✅ Monthly reports with HTML preview and PDF export (shows only jobs with submitted documents)
- ✅ Search and filter job entries
- ✅ Categories and tags for job organization
- ✅ Job templates for quick entry creation
- ✅ File attachments support
- ✅ Notifications for important dates (interviews, follow-ups, deadlines)
- ✅ Change history tracking (status changes only)
- ✅ Date validation (prevents setting status dates earlier than job creation date)
- ✅ Dark theme support
- ✅ Multilingual support (Russian, English, Deutsch)
- ✅ REST API v1 for integrations (Django REST Framework)

## Technologies

- Django 5.2.8
- ReportLab 4.0.9 (PDF generation)
- Django REST Framework 3.15.2
- django-filter 24.3
- Chart.js & FullCalendar.js (statistics & calendar)
- Bootstrap 5 (UI)
- SQLite (database)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sva273/job_search.git
cd job_search
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate  # For Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Tip:** if you installed the project earlier, re-run the command above to fetch newly added API dependencies (`djangorestframework`, `django-filter`).

### 3.5. Configure environment variables

Create a `.env` file in the project root with the following content:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

You can generate a new secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Compile translations

```bash
python manage.py compilemessages
```

### 7. Run development server

```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## Multilingual Support

The system supports three languages:
- **English** (en) - default language
- **Russian** (ru)
- **Deutsch** (de)

Language switching is available through the dropdown menu in the navigation bar.

## REST API v1

- Base URL: `http://127.0.0.1:8000/api/v1/`
- Authentication: Session & Basic auth
- Main resources:
  - `jobs/` — CRUD for job entries (search, filter, ordering, pagination)
  - `resume-status/` — resume submission status tracking
  - `categories/`, `tags/` — reference data
  - `templates/` — saved job templates
  - `attachments/` — upload & list attachments
  - `notifications/` — mark read, unread counter, bulk actions
  - `history/` — audit trail of job changes
  - `profile/` — user theme & reminder preferences
  - `statistics/` — comprehensive job statistics
  - `monthly-report/` — monthly reports with submitted documents
  - `calendar/` — calendar events (interviews, deadlines, follow-ups)

Detailed API documentation with request/response samples is available at `jobs/api/v1/README.md`.

## Project Structure

```
job_search/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── job_search/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── jobs/                # Main application
│   ├── api/             # REST API (versioned)
│   │   └── v1/
│   │       ├── serializers.py
│   │       ├── views/            # API Views (organized by functionality)
│   │       │   ├── __init__.py  # Exports all views
│   │       │   ├── view_jobs.py         # Job entries & resume statuses
│   │       │   ├── view_references.py   # Categories, tags, templates
│   │       │   ├── view_attachments.py  # File attachments
│   │       │   ├── view_notifications.py # Notifications
│   │       │   ├── view_profile.py      # User profile
│   │       │   └── view_statistics.py   # Statistics & reports
│   │       ├── urls.py
│   │       └── README.md
│   ├── models.py        # Data models
│   ├── views/            # Views (organized by functionality)
│   │   ├── __init__.py  # Exports all views
│   │   ├── view_auth.py        # Authentication & dashboard
│   │   ├── view_jobs.py         # Job entries CRUD
│   │   ├── view_statistics.py   # Statistics & reports
│   │   ├── view_calendar.py     # Calendar view
│   │   ├── view_templates.py    # Job templates
│   │   ├── view_attachments.py  # File attachments
│   │   ├── view_notifications.py # Notifications
│   │   ├── view_profile.py      # User profile & theme
│   │   ├── view_categories.py   # Categories management
│   │   └── view_tags.py         # Tags management
│   ├── forms/            # Forms (organized by functionality)
│   │   ├── __init__.py  # Exports all forms
│   │   ├── form_auth.py        # Authentication forms
│   │   ├── form_jobs.py         # Job entry forms
│   │   ├── form_templates.py    # Job template forms
│   │   ├── form_attachments.py  # Attachment forms
│   │   ├── form_categories.py   # Category forms
│   │   ├── form_tags.py         # Tag forms
│   │   └── form_profile.py      # User profile forms
│   ├── utils.py         # Helpers (statistics, formatting, etc.)
│   ├── validators.py    # Date validation functions
│   ├── pdf_generator.py # PDF generation
│   ├── signals.py       # Notifications & history hooks
│   └── urls.py          # URL routes
├── templates/           # HTML templates
│   ├── base.html
│   └── jobs/
├── jobs/static/         # CSS/JS assets (main.css, chart configs)
├── locale/              # Translations (en, ru, de)
└── media/               # Uploaded files
```

## Usage

### Registration

1. Go to the registration page
2. Fill in the form (username, email, password)
3. After registration, you will be automatically logged in

### Creating a Job Entry

1. Go to the "Jobs" section or click "Create Job" in the dashboard
2. Fill in the form with all job information:
   - Job Title
   - Employer
   - Address (optional)
   - Contacts: email, phone (optional)
   - Company website (optional)
   - Job URL
   - Description (optional)
3. Click "Save"

### Viewing and Managing Job Entries

- **Job List**: View all saved job entries with search and filtering
- **Job Details**: Detailed information about the job entry with all fields, resume submission status history, and change history
- **Edit**: Modify job entry data, application status, and add/remove resume submission statuses
- **Delete**: Remove a job entry
- **PDF Export**: Download job entry information as PDF
- **Dark Theme**: Toggle between light and dark themes in user profile settings

### Statistics

- **General Statistics**: Number of jobs, submitted resumes, received responses
- **Status Distribution**: Distribution of job entries by status
- **Success Rate**: Percentage of accepted and rejected applications
- **Time-based Statistics**: Activity for week, month, year
- **Top Employers**: List of employers with the most job entries
- **Monthly Reports**: View and download monthly reports showing all jobs with submitted documents (HTML preview + PDF export)
- **PDF Export**: Download complete statistics report as PDF

### Resume Submission Status Tracking

- Track detailed status history for each job application:
  - Resume Sent
  - Confirmation of Receipt Received
  - Interview Scheduled
  - Interview Passed
  - Another Interview Scheduled
  - Additional Documents Requested
  - Rejection Received
- Each status includes date/time and optional notes
- Automatic synchronization with main job status
- History of status changes (status changes only)
- **Date Validation**: System automatically validates that all status dates are not earlier than the job entry creation date. Invalid dates are automatically corrected or show validation errors with modal dialogs

### Job Sources

Supported job sources:
- LinkedIn
- Indeed
- StepStone
- XING
- Employment Agency
- Jobcenter
- Company Website
- Recruiter
- Referral
- Other

## Admin Panel

Access to admin panel: http://127.0.0.1:8000/admin/

Use superuser credentials to log in.

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations When Models Change

```bash
python manage.py makemigrations
python manage.py migrate
```

## Author

**Wjatscheslaw Schwab**

- GitHub: [@sva273](https://github.com/sva273)
- LinkedIn: [wjatscheslaw-schwab-15216a310](https://www.linkedin.com/in/wjatscheslaw-schwab-15216a310)


## License

This project is created for educational purposes.

## Support

If you encounter problems, check:
1. Are all dependencies installed
2. Are migrations applied
3. Are media file paths configured correctly
