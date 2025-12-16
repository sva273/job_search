from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_date_not_earlier_than_creation(date_value, created_at, field_label=None):
    """
    Validate that a date is not earlier than the job entry creation date.
    
    Args:
        date_value: The date to validate (datetime or None)
        created_at: The job entry creation date (datetime)
        field_label: Optional label for the field (for error messages)
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not date_value or not created_at:
        return True, None
    
    if date_value < created_at:
        if field_label:
            error_msg = _('%(field_label)s cannot be earlier than the job entry creation date (%(created_at)s)') % {
                'field_label': field_label,
                'created_at': created_at.strftime('%d.%m.%Y %H:%M')
            }
        else:
            error_msg = _('Date cannot be earlier than the job entry creation date (%(created_at)s)') % {
                'created_at': created_at.strftime('%d.%m.%Y %H:%M')
            }
        return False, error_msg
    
    return True, None


def get_valid_date(date_value, created_at, default=None):
    """
    Get a valid date that is not earlier than created_at.
    If date_value is earlier than created_at, returns created_at or default.
    
    Args:
        date_value: The date to validate (datetime or None)
        created_at: The job entry creation date (datetime)
        default: Default date to use if date_value is None (defaults to timezone.now())
        
    Returns:
        datetime: Valid date (not earlier than created_at)
    """
    if default is None:
        default = timezone.now()
    
    if not date_value:
        return max(created_at, default) if created_at else default
    
    if date_value < created_at:
        return created_at
    
    return date_value


def validate_job_entry_dates(job_entry):
    """
    Validate all date fields in JobEntry model.
    
    Args:
        job_entry: JobEntry instance to validate
        
    Returns:
        dict: Dictionary with field names as keys and error messages as values (empty if valid)
    """
    errors = {}
    
    # Get creation date
    if job_entry.pk:
        try:
            from .models import JobEntry
            original = JobEntry.objects.get(pk=job_entry.pk)
            created_at = original.created_at
        except JobEntry.DoesNotExist:
            created_at = job_entry.created_at
    else:
        created_at = job_entry.created_at or timezone.now()
    
    # Date fields to validate
    date_fields = {
        'resume_submitted_date': _('Resume Submitted Date'),
        'confirmation_date': _('Confirmation Date'),
        'response_date': _('Response Date'),
        'rejection_date': _('Rejection Date'),
        'interview_date': _('Interview Date'),
    }
    
    for field_name, field_label in date_fields.items():
        field_value = getattr(job_entry, field_name, None)
        is_valid, error_msg = validate_date_not_earlier_than_creation(
            field_value, created_at, field_label
        )
        if not is_valid:
            errors[field_name] = error_msg
    
    return errors


def auto_fix_job_entry_dates(job_entry):
    """
    Auto-fix dates in JobEntry that are earlier than created_at.
    Modifies the job_entry instance in place.
    
    Args:
        job_entry: JobEntry instance to fix
    """
    # Get creation date
    if job_entry.pk:
        try:
            from .models import JobEntry
            original = JobEntry.objects.get(pk=job_entry.pk)
            created_at = original.created_at
        except JobEntry.DoesNotExist:
            created_at = job_entry.created_at or timezone.now()
    else:
        created_at = job_entry.created_at or timezone.now()
    
    # Date fields to fix
    date_fields = ['resume_submitted_date', 'confirmation_date', 'response_date', 
                   'rejection_date', 'interview_date']
    
    for field_name in date_fields:
        field_value = getattr(job_entry, field_name, None)
        if field_value and field_value < created_at:
            setattr(job_entry, field_name, created_at)


def validate_resume_submission_status_date(resume_status):
    """
    Validate that ResumeSubmissionStatus date_time is not earlier than job_entry creation date.
    
    Args:
        resume_status: ResumeSubmissionStatus instance to validate
        
    Returns:
        dict: Dictionary with field names as keys and error messages as values (empty if valid)
    """
    errors = {}
    
    if resume_status.job_entry and resume_status.date_time:
        created_at = resume_status.job_entry.created_at
        is_valid, error_msg = validate_date_not_earlier_than_creation(
            resume_status.date_time, created_at
        )
        if not is_valid:
            errors['date_time'] = error_msg
    
    return errors


def get_valid_date_for_status_type(job_entry, status_type, fallback_date=None):
    """
    Get a valid date for a specific ResumeSubmissionStatus type.
    Uses the date from the latest ResumeSubmissionStatus of that type if available,
    otherwise uses fallback_date or created_at.
    
    Args:
        job_entry: JobEntry instance
        status_type: ResumeSubmissionStatus status_type
        fallback_date: Optional fallback date to use
        
    Returns:
        datetime: Valid date (not earlier than created_at)
    """
    from .models import ResumeSubmissionStatus
    
    # Get the latest ResumeSubmissionStatus for this type
    latest_status = ResumeSubmissionStatus.objects.filter(
        job_entry=job_entry,
        status_type=status_type
    ).order_by('-date_time').first()
    
    # If there's a latest_status, use its date (already validated at creation)
    if latest_status:
        if latest_status.date_time >= job_entry.created_at:
            return latest_status.date_time
        # If date is earlier than created_at, use created_at
        return job_entry.created_at
    
    # If no latest_status, use fallback_date or created_at
    if fallback_date and fallback_date >= job_entry.created_at:
        return fallback_date
    
    # If fallback_date is earlier than created_at or doesn't exist, use created_at
    return max(job_entry.created_at, timezone.now())


def validate_status_date_in_view(date_time, job_entry):
    """
    Validate status date in view before creating ResumeSubmissionStatus.
    Used in views/view_jobs.py.
    
    Args:
        date_time: datetime to validate
        job_entry: JobEntry instance
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not date_time or not job_entry:
        return True, None
    
    return validate_date_not_earlier_than_creation(
        date_time, job_entry.created_at
    )

