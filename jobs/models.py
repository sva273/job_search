from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .choices import (STATUS_CHOICES, PRIORITY_CHOICES, WORK_TYPE_CHOICES, SOURCE_CHOICES,
                      RESUME_SUBMISSION_STATUS_CHOICES)

# Create your models here.
class Category(models.Model):
    """Job category model"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    color = models.CharField(max_length=7, default='#667eea', verbose_name=_('Color'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tag model for job entries"""
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Tag Name'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class JobTemplate(models.Model):
    """Template for quick job entry creation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_templates')
    name = models.CharField(max_length=255, verbose_name=_('Template Name'))
    job_title = models.CharField(max_length=255, blank=True, verbose_name=_('Job Title'))
    employer = models.CharField(max_length=255, blank=True, verbose_name=_('Employer'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Job Template')
        verbose_name_plural = _('Job Templates')
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class JobEntry(models.Model):
    """Model for storing job vacancy information"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_entries')
    job_title = models.CharField(max_length=255, verbose_name=_('Job Title'))
    employer = models.CharField(max_length=255, verbose_name=_('Employer'))
    address = models.TextField(verbose_name=_('Address'), blank=True)
    contact_email = models.EmailField(verbose_name=_('Contact Email'), blank=True, null=True)
    contact_phone = models.CharField(max_length=50, verbose_name=_('Phone'), blank=True)
    company_website = models.URLField(verbose_name=_('Company Website'), blank=True, null=True)
    job_url = models.URLField(verbose_name=_('Job URL'))
    description = models.TextField(verbose_name=_('Description'), blank=True)
    
    # Categories and tags
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('Tags'))
    
    # Additional fields
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     verbose_name=_('Salary Min'))
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     verbose_name=_('Salary Max'))
    salary_currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, blank=True, verbose_name=_('Work Type'))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name=_('Priority'))
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True, verbose_name=_('Source'))
    
    # Calendar and reminders
    interview_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Interview Date'))
    follow_up_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Follow-up Date'))
    application_deadline = models.DateField(blank=True, null=True, verbose_name=_('Application Deadline'))
    reminder_sent = models.BooleanField(default=False, verbose_name=_('Reminder Sent'))
    
    # Fields for tracking resume submission
    resume_submitted = models.BooleanField(default=False, verbose_name=_('Resume Submitted'))
    resume_submitted_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Resume Submitted Date'))
    application_confirmed = models.BooleanField(default=False, verbose_name=_('Application Confirmed'))
    confirmation_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Confirmation Date'))
    response_received = models.BooleanField(default=False, verbose_name=_('Response Received'))
    response_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Response Date'))
    rejection_received = models.BooleanField(default=False, verbose_name=_('Rejection Received'))
    rejection_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Rejection Date'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_applied', verbose_name=_('Status'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Job Entry')
        verbose_name_plural = _('Job Entries')
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['user', '-created_at']),  # Composite index for user's jobs
            models.Index(fields=['user', 'status']),  # Composite index for filtering by user and status
            models.Index(fields=['work_type']),
            models.Index(fields=['source']),
            models.Index(fields=['employer']),  # For search optimization
        ]
    
    def clean(self):
        """Validate that status dates are not earlier than creation date"""
        from django.core.exceptions import ValidationError
        from .validators import validate_job_entry_dates
        
        errors = validate_job_entry_dates(self)
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation and auto-fix dates if needed"""
        from .validators import auto_fix_job_entry_dates
        
        # Auto-fix dates that are earlier than created_at
        auto_fix_job_entry_dates(self)
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.job_title} - {self.employer}"


class ResumeSubmissionStatus(models.Model):
    """Status of resume submission for a job entry"""
    job_entry = models.ForeignKey(JobEntry, on_delete=models.CASCADE, related_name='resume_statuses',
                                  verbose_name=_('Job Entry'))
    status_type = models.CharField(max_length=50, choices=RESUME_SUBMISSION_STATUS_CHOICES,
                                   verbose_name=_('Status Type'))
    date_time = models.DateTimeField(verbose_name=_('Date and Time'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Resume Submission Status')
        verbose_name_plural = _('Resume Submission Statuses')
        ordering = ['-date_time']
        indexes = [
            models.Index(fields=['job_entry', '-date_time']),
        ]
    
    def clean(self):
        """Validate that date_time is not earlier than job_entry creation date"""
        from django.core.exceptions import ValidationError
        from .validators import validate_resume_submission_status_date
        
        errors = validate_resume_submission_status_date(self)
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to call clean validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return (f"{self.get_status_type_display()} - {self.job_entry.job_title} - "
                f"{self.date_time.strftime('%d.%m.%Y %H:%M')}")


class JobEntryHistory(models.Model):
    """History of changes to job entries"""
    job_entry = models.ForeignKey(JobEntry, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field_name = models.CharField(max_length=100, verbose_name=_('Field Name'))
    old_value = models.TextField(blank=True, verbose_name=_('Old Value'))
    new_value = models.TextField(blank=True, verbose_name=_('New Value'))
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Changed At'))
    
    class Meta:
        verbose_name = _('Job Entry History')
        verbose_name_plural = _('Job Entry Histories')
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.job_entry} - {self.field_name} - {self.changed_at}"


class Attachment(models.Model):
    """File attachments for job entries"""
    job_entry = models.ForeignKey(JobEntry, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', verbose_name=_('File'))
    file_name = models.CharField(max_length=255, verbose_name=_('File Name'))
    file_type = models.CharField(max_length=50, blank=True, verbose_name=_('File Type'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('Description'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))
    
    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.job_entry}"


class Notification(models.Model):
    """Notifications for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    job_entry = models.ForeignKey(JobEntry, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='notifications')
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    message = models.TextField(verbose_name=_('Message'))
    notification_type = models.CharField(max_length=50, default='info', verbose_name=_('Type'))
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),  # Composite index for user's notifications
            models.Index(fields=['user', 'is_read']),  # For filtering unread notifications
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user}"


class UserProfile(models.Model):
    """User profile with preferences"""
    THEME_CHOICES = [
        ('light', _('Light')),
        ('dark', _('Dark')),
        ('auto', _('Auto')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=150, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=150, blank=True, verbose_name=_('Last Name'))
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light', verbose_name=_('Theme'))
    email_notifications_enabled = models.BooleanField(default=True, verbose_name=_('Email Notifications Enabled'))
    reminder_days_before = models.IntegerField(default=1, verbose_name=_('Reminder Days Before'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def get_full_name(self):
        """Get full name or fallback to username"""
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.user.username
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.theme}"

