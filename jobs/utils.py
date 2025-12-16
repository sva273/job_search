from django.db.models import Count, Avg
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.formats import date_format
from django.utils.translation import gettext as translation_gettext
from datetime import timedelta
from .models import JobEntry, ResumeSubmissionStatus


def sync_status_from_resume_status(job_entry, resume_status_type):
    """
    Синхронизирует общий status и флаги JobEntry на основе типа ResumeSubmissionStatus.
    
    Args:
        job_entry: JobEntry instance
        resume_status_type: тип статуса из RESUME_SUBMISSION_STATUS_CHOICES
    """
    # Используем валидатор для получения валидной даты
    from .validators import get_valid_date_for_status_type as validator_get_valid_date
    
    # Маппинг типов статусов на общий status и флаги
    status_mapping = {
        'resume_sent': {
            'status': 'applied',
            'resume_submitted': True,
            'resume_submitted_date': validator_get_valid_date(job_entry, 'resume_sent', job_entry.resume_submitted_date),
        },
        'confirmation_received': {
            'status': 'confirmed',
            'application_confirmed': True,
            'confirmation_date': validator_get_valid_date(job_entry, 'confirmation_received', job_entry.confirmation_date),
        },
        'interview_scheduled': {
            # Интервью запланировано - устанавливаем специальный статус
            'status': 'interview_scheduled',
            'application_confirmed': True,  # Заявка подтверждена, раз интервью запланировано
            'response_received': True,  # Получен ответ, раз интервью запланировано
            'response_date': validator_get_valid_date(job_entry, 'interview_scheduled', job_entry.response_date),
        },
        'interview_passed': {
            # Интервью пройдено - устанавливаем специальный статус
            'status': 'interview_passed',
            'response_received': True,
            'response_date': validator_get_valid_date(job_entry, 'interview_passed', job_entry.response_date),
        },
        'another_interview_scheduled': {
            # Еще одно интервью запланировано - используем статус interview_scheduled
            'status': 'interview_scheduled',
            'application_confirmed': True,
            'response_received': True,
            'response_date': validator_get_valid_date(job_entry, 'another_interview_scheduled', job_entry.response_date),
        },
        'documents_requested': {
            # Запрошены документы - устанавливаем специальный статус
            'status': 'documents_requested',
            'response_received': True,
            'response_date': validator_get_valid_date(job_entry, 'documents_requested', job_entry.response_date),
        },
        'rejection_received': {
            'status': 'rejected',
            'rejection_received': True,
            'rejection_date': validator_get_valid_date(job_entry, 'rejection_received', job_entry.rejection_date),
        },
    }
    
    if resume_status_type in status_mapping:
        mapping = status_mapping[resume_status_type]
        
        # Always update status from mapping
        if 'status' in mapping:
            job_entry.status = mapping['status']
        
        if 'resume_submitted' in mapping:
            job_entry.resume_submitted = mapping['resume_submitted']
        if 'resume_submitted_date' in mapping:
            job_entry.resume_submitted_date = mapping['resume_submitted_date']
        if 'application_confirmed' in mapping:
            job_entry.application_confirmed = mapping['application_confirmed']
        if 'confirmation_date' in mapping:
            job_entry.confirmation_date = mapping['confirmation_date']
        if 'response_received' in mapping:
            job_entry.response_received = mapping['response_received']
        if 'response_date' in mapping:
            job_entry.response_date = mapping['response_date']
        if 'rejection_received' in mapping:
            job_entry.rejection_received = mapping['rejection_received']
        if 'rejection_date' in mapping:
            job_entry.rejection_date = mapping['rejection_date']


def sync_resume_status_from_flags(job_entry, changed_field):
    """
    Создает ResumeSubmissionStatus на основе измененных флагов.
    
    Args:
        job_entry: JobEntry instance
        changed_field: имя измененного поля ('resume_submitted', 'application_confirmed', etc.)
    """
    # Определяем тип статуса на основе измененного поля
    status_type_mapping = {
        'resume_submitted': 'resume_sent',
        'application_confirmed': 'confirmation_received',
        'rejection_received': 'rejection_received',
        # response_received не имеет прямого соответствия в RESUME_SUBMISSION_STATUS_CHOICES,
        # поэтому пропускаем его - он будет обработан через общий status
    }
    
    if changed_field in status_type_mapping:
        status_type = status_type_mapping[changed_field]
        
        # Определяем дату для статуса
        # Убеждаемся, что дата не раньше created_at
        date_mapping = {
            'resume_submitted': job_entry.resume_submitted_date or timezone.now(),
            'application_confirmed': job_entry.confirmation_date or timezone.now(),
            'rejection_received': job_entry.rejection_date or timezone.now(),
        }
        
        date_time = date_mapping.get(changed_field, timezone.now())
        # Убеждаемся, что дата не раньше created_at
        if date_time < job_entry.created_at:
            date_time = job_entry.created_at
        
        # Проверяем, нет ли уже такого статуса с такой же датой (чтобы избежать дубликатов)
        existing = ResumeSubmissionStatus.objects.filter(
            job_entry=job_entry,
            status_type=status_type,
            date_time__date=date_time.date()
        ).first()
        
        if not existing:
            ResumeSubmissionStatus.objects.create(
                job_entry=job_entry,
                status_type=status_type,
                date_time=date_time,
                notes=''
            )


def sync_resume_status_from_general_status(job_entry, new_status):
    """
    Создает ResumeSubmissionStatus на основе общего статуса.
    
    Args:
        job_entry: JobEntry instance
        new_status: новый общий статус
    """
    # Маппинг общего статуса на тип ResumeSubmissionStatus
    status_to_resume_status = {
        'applied': 'resume_sent',
        'confirmed': 'confirmation_received',
        'rejected': 'rejection_received',
        # response_received и accepted не имеют прямого соответствия в RESUME_SUBMISSION_STATUS_CHOICES
    }
    
    if new_status in status_to_resume_status:
        status_type = status_to_resume_status[new_status]
        
        # Определяем дату
        from .validators import get_valid_date
        date_mapping = {
            'applied': job_entry.resume_submitted_date,
            'confirmed': job_entry.confirmation_date,
            'rejected': job_entry.rejection_date,
        }
        
        date_time = get_valid_date(
            date_mapping.get(new_status),
            job_entry.created_at,
            default=timezone.now()
        )
        
        # Проверяем, нет ли уже такого статуса
        existing = ResumeSubmissionStatus.objects.filter(
            job_entry=job_entry,
            status_type=status_type,
            date_time__date=date_time.date()
        ).first()
        
        if not existing:
            ResumeSubmissionStatus.objects.create(
                job_entry=job_entry,
                status_type=status_type,
                date_time=date_time,
                notes=''
            )


def get_user_display_name(user):
    """
    Get user's display name (full name from profile or username as fallback)
    
    Args:
        user: User instance
        
    Returns:
        str: Full name or username
    """
    if hasattr(user, 'profile'):
        profile = user.profile
        if profile.first_name or profile.last_name:
            return f"{profile.first_name} {profile.last_name}".strip()
    # Fallback to username
    return user.username


def get_statistics_data(user_jobs):
    """
    Calculate statistics for user's job entries.
    Returns a dictionary with all statistics.
    """
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    year_ago = now - timedelta(days=365)
    
    # General statistics
    total_jobs = user_jobs.count()
    
    # Statistics by category, priority, work type, source
    category_stats = list(user_jobs.values('category__name').annotate(count=Count('id')).order_by('-count'))
    priority_stats = list(user_jobs.values('priority').annotate(count=Count('id')).order_by('priority'))
    work_type_stats = list(user_jobs.values('work_type').annotate(count=Count('id')).order_by('-count'))
    source_stats = list(user_jobs.values('source').annotate(count=Count('id')).order_by('-count'))
    
    # Status statistics
    status_stats = user_jobs.values('status').annotate(count=Count('id')).order_by('status')
    status_dict = {item['status']: item['count'] for item in status_stats}
    
    not_applied = status_dict.get('not_applied', 0)
    applied = status_dict.get('applied', 0)
    confirmed = status_dict.get('confirmed', 0)
    response_received = status_dict.get('response_received', 0)
    rejected = status_dict.get('rejected', 0)
    accepted = status_dict.get('accepted', 0)
    
    # Flag-based statistics
    resume_submitted_count = user_jobs.filter(resume_submitted=True).count()
    application_confirmed_count = user_jobs.filter(application_confirmed=True).count()
    response_received_count = user_jobs.filter(response_received=True).count()
    rejection_received_count = user_jobs.filter(rejection_received=True).count()
    
    # Time-based statistics
    jobs_last_week = user_jobs.filter(created_at__gte=week_ago).count()
    jobs_last_month = user_jobs.filter(created_at__gte=month_ago).count()
    jobs_last_year = user_jobs.filter(created_at__gte=year_ago).count()
    
    # Resume submission statistics
    resumes_submitted_last_week = user_jobs.filter(
        resume_submitted=True,
        resume_submitted_date__gte=week_ago
    ).count()
    resumes_submitted_last_month = user_jobs.filter(
        resume_submitted=True,
        resume_submitted_date__gte=month_ago
    ).count()
    resumes_submitted_last_year = user_jobs.filter(
        resume_submitted=True,
        resume_submitted_date__gte=year_ago
    ).count()
    
    # Response statistics
    responses_last_week = user_jobs.filter(
        response_received=True,
        response_date__gte=week_ago
    ).count()
    responses_last_month = user_jobs.filter(
        response_received=True,
        response_date__gte=month_ago
    ).count()
    responses_last_year = user_jobs.filter(
        response_received=True,
        response_date__gte=year_ago
    ).count()
    
    # Rejection statistics
    rejections_last_week = user_jobs.filter(
        rejection_received=True,
        rejection_date__gte=week_ago
    ).count()
    rejections_last_month = user_jobs.filter(
        rejection_received=True,
        rejection_date__gte=month_ago
    ).count()
    rejections_last_year = user_jobs.filter(
        rejection_received=True,
        rejection_date__gte=year_ago
    ).count()
    
    # Success and rejection rates
    success_rate = round((accepted / resume_submitted_count) * 100, 1) if resume_submitted_count > 0 else 0
    rejection_rate = round((rejection_received_count / resume_submitted_count) * 100, 1) if resume_submitted_count > 0 else 0
    
    # Top employers
    top_employers = list(user_jobs.values('employer').annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    # Monthly statistics (last 12 months)
    monthly_stats = []
    for i in range(11, -1, -1):
        month_start = now - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)
        month_jobs = user_jobs.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'count': month_jobs
        })
    
    # Salary statistics
    jobs_with_salary = user_jobs.exclude(salary_min__isnull=True)
    avg_salary_min = jobs_with_salary.aggregate(avg=Avg('salary_min'))['avg'] or 0
    avg_salary_max = jobs_with_salary.aggregate(avg=Avg('salary_max'))['avg'] or 0
    
    # Upcoming events
    upcoming_interviews = user_jobs.filter(interview_date__gte=now).exclude(interview_date__isnull=True).count()
    upcoming_follow_ups = user_jobs.filter(follow_up_date__gte=now).exclude(follow_up_date__isnull=True).count()
    upcoming_deadlines = user_jobs.filter(application_deadline__gte=now.date()).exclude(application_deadline__isnull=True).count()
    
    return {
        'total_jobs': total_jobs,
        'not_applied': not_applied,
        'applied': applied,
        'confirmed': confirmed,
        'response_received': response_received,
        'rejected': rejected,
        'accepted': accepted,
        'resume_submitted_count': resume_submitted_count,
        'application_confirmed_count': application_confirmed_count,
        'response_received_count': response_received_count,
        'rejection_received_count': rejection_received_count,
        'jobs_last_week': jobs_last_week,
        'jobs_last_month': jobs_last_month,
        'jobs_last_year': jobs_last_year,
        'resumes_submitted_last_week': resumes_submitted_last_week,
        'resumes_submitted_last_month': resumes_submitted_last_month,
        'resumes_submitted_last_year': resumes_submitted_last_year,
        'responses_last_week': responses_last_week,
        'responses_last_month': responses_last_month,
        'responses_last_year': responses_last_year,
        'rejections_last_week': rejections_last_week,
        'rejections_last_month': rejections_last_month,
        'rejections_last_year': rejections_last_year,
        'success_rate': success_rate,
        'rejection_rate': rejection_rate,
        'top_employers': top_employers,
        'monthly_stats': monthly_stats,
        'category_stats': category_stats,
        'priority_stats': priority_stats,
        'work_type_stats': work_type_stats,
        'source_stats': source_stats,
        'avg_salary_min': round(avg_salary_min, 2),
        'avg_salary_max': round(avg_salary_max, 2),
        'upcoming_interviews': upcoming_interviews,
        'upcoming_follow_ups': upcoming_follow_ups,
        'upcoming_deadlines': upcoming_deadlines,
    }


def format_date_string(date_str):
    """Format date string to readable format"""
    if not date_str or date_str == 'None' or date_str == '':
        return None
    try:
        # Try parsing as datetime first
        dt = parse_datetime(str(date_str))
        if dt:
            return date_format(dt, format='d.m.Y H:i')
        # Try parsing as date
        d = parse_date(str(date_str))
        if d:
            return date_format(d, format='d.m.Y')
    except:
        pass
    return date_str


def translate_choice_value(field_name, value):
    """Translate choice field values (status, priority, work_type, source)"""
    if not value or value == '' or value == 'None':
        return None
    
    translations = {
        'status': {
            'not_applied': translation_gettext('Not Applied'),
            'applied': translation_gettext('Applied'),
            'confirmed': translation_gettext('Application Confirmed'),
            'response_received': translation_gettext('Response Received'),
            'rejected': translation_gettext('Rejected'),
            'accepted': translation_gettext('Accepted'),
        },
        'priority': {
            'high': translation_gettext('High'),
            'medium': translation_gettext('Medium'),
            'low': translation_gettext('Low'),
        },
        'work_type': {
            'remote': translation_gettext('Remote'),
            'office': translation_gettext('Office'),
            'home_office': translation_gettext('Home Office'),
            'hybrid': translation_gettext('Hybrid'),
            'flexible': translation_gettext('Flexible'),
        },
        'source': {
            'linkedin': translation_gettext('LinkedIn'),
            'indeed': translation_gettext('Indeed'),
            'stepstone': translation_gettext('StepStone'),
            'xing': translation_gettext('XING'),
            'employment_agency': translation_gettext('Employment Agency'),
            'jobcenter': translation_gettext('Jobcenter'),
            'company_website': translation_gettext('Company Website'),
            'recruiter': translation_gettext('Recruiter'),
            'referral': translation_gettext('Referral'),
            'other': translation_gettext('Other'),
        },
    }
    
    return translations.get(field_name, {}).get(value, value)


def format_history_item(history_item):
    """Format and translate history item for display"""
    field_name_translations = {
        'status': translation_gettext('Status'),
        'job_title': translation_gettext('Job Title'),
        'employer': translation_gettext('Employer'),
        'priority': translation_gettext('Priority'),
        'category': translation_gettext('Category'),
        'resume_submitted': translation_gettext('Resume Submitted'),
        'application_confirmed': translation_gettext('Application Confirmed'),
        'response_received': translation_gettext('Response Received'),
        'rejection_received': translation_gettext('Rejection Received'),
        'interview_date': translation_gettext('Interview Date'),
        'follow_up_date': translation_gettext('Follow-up Date'),
        'application_deadline': translation_gettext('Application Deadline'),
    }
    
    boolean_fields = ['resume_submitted', 'application_confirmed', 'response_received', 'rejection_received']
    date_fields = ['interview_date', 'follow_up_date', 'application_deadline', 
                   'resume_submitted_date', 'confirmation_date', 'response_date', 'rejection_date']
    
    # Set translated field name
    history_item.translated_field_name = field_name_translations.get(
        history_item.field_name,
        history_item.field_name.replace('_', ' ').title()
    )
    
    # Format boolean values
    if history_item.field_name in boolean_fields:
        history_item.translated_old_value = _format_boolean_value(history_item.old_value)
        history_item.translated_new_value = _format_boolean_value(history_item.new_value)
    # Format date values
    elif history_item.field_name in date_fields:
        history_item.translated_old_value = format_date_string(history_item.old_value)
        history_item.translated_new_value = format_date_string(history_item.new_value)
    # Translate choice fields
    elif history_item.field_name in ['status', 'priority', 'work_type', 'source']:
        history_item.translated_old_value = translate_choice_value(history_item.field_name, history_item.old_value)
        history_item.translated_new_value = translate_choice_value(history_item.field_name, history_item.new_value)
    # Other fields
    else:
        history_item.translated_old_value = _format_generic_value(history_item.old_value)
        history_item.translated_new_value = _format_generic_value(history_item.new_value)
    
    return history_item


def _format_boolean_value(value):
    """Format boolean value for display"""
    if not value or value == '' or value == 'None':
        return None
    if value.lower() == 'true' or value == 'True':
        return translation_gettext('Yes')
    if value.lower() == 'false' or value == 'False':
        return translation_gettext('No')
    return value


def _format_generic_value(value):
    """Format generic value for display"""
    if not value or value == '' or value == 'None':
        return None
    return value
