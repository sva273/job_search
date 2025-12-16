"""
API Views package - organized by functionality
All views are imported here for backward compatibility
"""
from .view_jobs import (
    JobEntryViewSet, ResumeSubmissionStatusViewSet, JobEntryHistoryViewSet
)
from .view_references import (
    CategoryViewSet, TagViewSet, JobTemplateViewSet
)
from .view_attachments import AttachmentViewSet
from .view_notifications import NotificationViewSet
from .view_profile import UserProfileViewSet
from .view_statistics import StatisticsView, MonthlyReportView, CalendarView

__all__ = [
    # Jobs
    'JobEntryViewSet',
    'ResumeSubmissionStatusViewSet',
    'JobEntryHistoryViewSet',
    # References
    'CategoryViewSet',
    'TagViewSet',
    'JobTemplateViewSet',
    # Attachments
    'AttachmentViewSet',
    # Notifications
    'NotificationViewSet',
    # Profile
    'UserProfileViewSet',
    # Statistics
    'StatisticsView',
    'MonthlyReportView',
    'CalendarView',
]

