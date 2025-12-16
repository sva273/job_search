"""
Views package - organized by functionality
All views are imported here for backward compatibility with urls.py
"""
from .view_auth import register, dashboard
from .view_jobs import (
    create_job, job_list, job_detail, edit_job, delete_job,
    download_job_pdf, add_resume_status, delete_resume_status
)
from .view_statistics import (
    statistics, download_statistics_pdf, monthly_report, monthly_report_pdf
)
from .view_calendar import calendar_view
from .view_templates import (
    job_templates, create_from_template, edit_template, delete_template
)
from .view_attachments import upload_attachment, delete_attachment
from .view_notifications import (
    notifications, mark_notification_read, delete_notification, delete_all_notifications
)
from .view_profile import toggle_theme, edit_profile
from .view_categories import (
    categories_list, create_category, edit_category, delete_category
)
from .view_tags import tags_list, create_tag, edit_tag, delete_tag

__all__ = [
    # Auth
    'register', 'dashboard',
    # Jobs
    'create_job', 'job_list', 'job_detail', 'edit_job', 'delete_job',
    'download_job_pdf', 'add_resume_status', 'delete_resume_status',
    # Statistics
    'statistics', 'download_statistics_pdf', 'monthly_report', 'monthly_report_pdf',
    # Calendar
    'calendar_view',
    # Templates
    'job_templates', 'create_from_template', 'edit_template', 'delete_template',
    # Attachments
    'upload_attachment', 'delete_attachment',
    # Notifications
    'notifications', 'mark_notification_read', 'delete_notification', 'delete_all_notifications',
    # Profile
    'toggle_theme', 'edit_profile',
    # Categories
    'categories_list', 'create_category', 'edit_category', 'delete_category',
    # Tags
    'tags_list', 'create_tag', 'edit_tag', 'delete_tag',
]

