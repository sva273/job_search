"""
Forms package - organized by functionality
All forms are imported here for backward compatibility
"""
from .form_auth import UserRegistrationForm
from .form_jobs import JobEntryForm, ResumeSubmissionStatusForm
from .form_templates import JobTemplateForm
from .form_attachments import AttachmentForm
from .form_categories import CategoryForm
from .form_tags import TagForm
from .form_profile import UserProfileForm

__all__ = [
    'UserRegistrationForm',
    'JobEntryForm',
    'ResumeSubmissionStatusForm',
    'JobTemplateForm',
    'AttachmentForm',
    'CategoryForm',
    'TagForm',
    'UserProfileForm',
]

