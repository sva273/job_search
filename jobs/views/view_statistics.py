from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import JobEntry
from ..pdf_generator import generate_statistics_pdf, generate_monthly_report_pdf
from ..utils import get_statistics_data, get_user_display_name


@login_required
def statistics(request):
    """Complete statistics for job entries with advanced analytics"""
    user_jobs = JobEntry.objects.filter(user=request.user).select_related('category').only(
        'id', 'status', 'resume_submitted', 'response_received', 'rejection_received',
        'created_at', 'resume_submitted_date', 'response_date', 'rejection_date',
        'employer', 'category__name'
    )
    context = get_statistics_data(user_jobs)
    return render(request, 'jobs/statistics.html', context)


@login_required

def download_statistics_pdf(request):
    """Download PDF file with statistics"""
    user_jobs = JobEntry.objects.filter(user=request.user)
    statistics_data = get_statistics_data(user_jobs)
    
    try:
        # Get current user language
        from django.utils.translation import get_language
        language_code = get_language() or 'ru'
        user_display_name = get_user_display_name(request.user)
        pdf_buffer = generate_statistics_pdf(statistics_data, user_display_name, language_code)
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        filename = f"statistics_{request.user.username}_{timezone.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, _('Error generating PDF: %(error)s') % {'error': str(e)})
        return redirect('jobs:statistics')



def _get_monthly_report_job_entries(user, year, month):
    """Helper function to get filtered and sorted job entries for monthly report"""
    from datetime import datetime
    from calendar import monthrange
    
    # Get first and last day of the month
    first_day = timezone.make_aware(datetime(year, month, 1))
    last_day_num = monthrange(year, month)[1]
    last_day = timezone.make_aware(datetime(year, month, last_day_num, 23, 59, 59))
    
    # Filter job entries for the month by application submission date
    # Include ONLY entries where documents were actually submitted:
    # 1. resume_submitted_date is in the month, OR
    # 2. There's a ResumeSubmissionStatus with status_type='resume_sent' in the month
    # Exclude entries with status='not_applied' as they don't have submitted documents
    
    # Get IDs from both querysets to avoid union issues
    entries_by_date_ids = set(JobEntry.objects.filter(
        user=user,
        resume_submitted_date__gte=first_day,
        resume_submitted_date__lte=last_day
    ).exclude(resume_submitted_date__isnull=True).exclude(status='not_applied').values_list('id', flat=True))
    
    entries_by_status_ids = set(JobEntry.objects.filter(
        user=user,
        resume_statuses__status_type='resume_sent',
        resume_statuses__date_time__gte=first_day,
        resume_statuses__date_time__lte=last_day
    ).exclude(status='not_applied').values_list('id', flat=True))
    
    # Combine IDs and get all job entries
    all_ids = entries_by_date_ids | entries_by_status_ids
    
    # Get job entries with prefetch for performance
    # Additional filter: exclude entries that don't have any resume submission evidence
    job_entries = list(JobEntry.objects.filter(
        id__in=all_ids
    ).prefetch_related('resume_statuses', 'history').exclude(
        status='not_applied'
    ))
    
    # Final filter: ensure each entry has evidence of document submission
    # Either has resume_submitted_date OR has ResumeSubmissionStatus with 'resume_sent'
    filtered_entries = []
    for job in job_entries:
        has_resume_submitted_date = job.resume_submitted_date is not None
        has_resume_sent_status = job.resume_statuses.filter(status_type='resume_sent').exists()
        
        if has_resume_submitted_date or has_resume_sent_status:
            filtered_entries.append(job)
    
    job_entries = filtered_entries
    
    # Sort by date: use resume_submitted_date if available, otherwise use date from ResumeSubmissionStatus
    def get_sort_date(job):
        if job.resume_submitted_date:
            return job.resume_submitted_date
        # Try to get date from ResumeSubmissionStatus
        try:
            resume_status = job.resume_statuses.filter(status_type='resume_sent').order_by('date_time').first()
            if resume_status:
                return resume_status.date_time
        except Exception:
            pass
        # Fallback to created_at
        return job.created_at or timezone.now()
    
    job_entries.sort(key=get_sort_date)
    return job_entries



def _parse_year_month(request):
    """Helper function to parse year and month from request"""
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    # If not provided, use current month
    if not year or not month:
        now = timezone.now()
        year = now.year
        month = now.month
    else:
        try:
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                month = timezone.now().month
        except (ValueError, TypeError):
            now = timezone.now()
            year = now.year
            month = now.month
    
    return year, month


@login_required

def monthly_report(request):
    """Display monthly report HTML page"""
    year, month = _parse_year_month(request)
    job_entries = _get_monthly_report_job_entries(request.user, year, month)
    
    # Get month name for display
    from django.utils.translation import get_language
    language_code = get_language() or getattr(request, 'LANGUAGE_CODE', None) or 'en'
    from django.utils import translation
    old_language = translation.get_language()
    translation.activate(language_code)
    
    month_names = {
        1: translation.gettext('January'), 2: translation.gettext('February'),
        3: translation.gettext('March'), 4: translation.gettext('April'),
        5: translation.gettext('May'), 6: translation.gettext('June'),
        7: translation.gettext('July'), 8: translation.gettext('August'),
        9: translation.gettext('September'), 10: translation.gettext('October'),
        11: translation.gettext('November'), 12: translation.gettext('December')
    }
    month_name = month_names.get(month, str(month))
    
    # Get status translations
    from ..choices import STATUS_CHOICES
    status_dict = {}
    for key, label in STATUS_CHOICES:
        status_dict[key] = str(label)
    
    # Prepare data for template
    report_data = []
    for job in job_entries:
        # Get submission date
        date_str = _('Not specified')
        if job.resume_submitted_date:
            date_str = job.resume_submitted_date.strftime('%d.%m.%Y')
        else:
            try:
                resume_status = job.resume_statuses.filter(status_type='resume_sent').order_by('date_time').first()
                if resume_status:
                    date_str = resume_status.date_time.strftime('%d.%m.%Y')
                elif job.resume_submitted and job.created_at:
                    date_str = job.created_at.strftime('%d.%m.%Y')
            except Exception:
                if job.created_at:
                    date_str = job.created_at.strftime('%d.%m.%Y')
        
        # Get result date - date when status was changed
        # Priority: 1) JobEntryHistory (most accurate), 2) ResumeSubmissionStatus, 3) Model date fields
        result_date_str = _('Not specified')
        try:
            # First, try to get date from JobEntryHistory (most accurate)
            status_history = job.history.filter(field_name='status').order_by('-changed_at').first()
            if status_history:
                result_date_str = status_history.changed_at.strftime('%d.%m.%Y')
            else:
                # Fallback: try ResumeSubmissionStatus - map JobEntry.status to ResumeSubmissionStatus.status_type
                status_mapping = {
                    'rejected': ['rejection_received'],
                    'response_received': ['response_received'],
                    'interview_scheduled': ['interview_scheduled', 'another_interview_scheduled'],
                    'interview_passed': ['interview_passed'],
                    'documents_requested': ['documents_requested'],
                    'accepted': ['response_received'],  # Accepted uses response_received status
                    'confirmed': ['confirmation_received'],
                    'applied': ['resume_sent'],
                }
                
                # Get all possible status types for current job status
                status_types_to_find = status_mapping.get(job.status, [])
                
                # Try to find the latest ResumeSubmissionStatus for any of the mapped types
                latest_status = None
                if status_types_to_find:
                    latest_status = job.resume_statuses.filter(
                        status_type__in=status_types_to_find
                    ).order_by('-date_time').first()
                
                if latest_status:
                    result_date_str = latest_status.date_time.strftime('%d.%m.%Y')
                else:
                    # Final fallback: use model date fields
                    if job.status == 'rejected' and job.rejection_date:
                        result_date_str = job.rejection_date.strftime('%d.%m.%Y')
                    elif job.status in ['response_received', 'accepted', 'interview_scheduled', 'interview_passed', 'documents_requested'] and job.response_date:
                        result_date_str = job.response_date.strftime('%d.%m.%Y')
                    elif job.status in ['interview_scheduled', 'interview_passed'] and job.interview_date:
                        result_date_str = job.interview_date.strftime('%d.%m.%Y')
                    elif job.status == 'confirmed' and job.confirmation_date:
                        result_date_str = job.confirmation_date.strftime('%d.%m.%Y')
                    elif job.status == 'applied' and job.resume_submitted_date:
                        result_date_str = job.resume_submitted_date.strftime('%d.%m.%Y')
        except Exception:
            # Fallback on error - try same logic but with error handling
            try:
                status_history = job.history.filter(field_name='status').order_by('-changed_at').first()
                if status_history:
                    result_date_str = status_history.changed_at.strftime('%d.%m.%Y')
                else:
                    # Try ResumeSubmissionStatus
                    status_mapping = {
                        'rejected': ['rejection_received'],
                        'response_received': ['response_received'],
                        'interview_scheduled': ['interview_scheduled', 'another_interview_scheduled'],
                        'interview_passed': ['interview_passed'],
                        'documents_requested': ['documents_requested'],
                        'accepted': ['response_received'],
                        'confirmed': ['confirmation_received'],
                        'applied': ['resume_sent'],
                    }
                    status_types_to_find = status_mapping.get(job.status, [])
                    if status_types_to_find:
                        latest_status = job.resume_statuses.filter(
                            status_type__in=status_types_to_find
                        ).order_by('-date_time').first()
                        if latest_status:
                            result_date_str = latest_status.date_time.strftime('%d.%m.%Y')
                    
                    # Fallback to model fields
                    if result_date_str == _('Not specified'):
                        if job.status == 'rejected' and job.rejection_date:
                            result_date_str = job.rejection_date.strftime('%d.%m.%Y')
                        elif job.status in ['response_received', 'accepted', 'interview_scheduled', 'interview_passed', 'documents_requested'] and job.response_date:
                            result_date_str = job.response_date.strftime('%d.%m.%Y')
                        elif job.status in ['interview_scheduled', 'interview_passed'] and job.interview_date:
                            result_date_str = job.interview_date.strftime('%d.%m.%Y')
                        elif job.status == 'confirmed' and job.confirmation_date:
                            result_date_str = job.confirmation_date.strftime('%d.%m.%Y')
                        elif job.status == 'applied' and job.resume_submitted_date:
                            result_date_str = job.resume_submitted_date.strftime('%d.%m.%Y')
            except Exception:
                pass
        
        report_data.append({
            'date': date_str,
            'employer': job.employer or _('Not specified'),
            'job_title': job.job_title or _('Not specified'),
            'email': job.contact_email or _('Not specified'),
            'status': status_dict.get(job.status, job.status),
            'status_key': job.status,  # Add status key for template logic
            'result_date': result_date_str,
        })
    
    translation.activate(old_language)
    
    context = {
        'job_entries': report_data,
        'year': year,
        'month': month,
        'month_name': month_name,
        'user_display_name': get_user_display_name(request.user),
        'user_theme': getattr(request.user, 'userprofile', None) and request.user.userprofile.theme or 'light',
    }
    
    return render(request, 'jobs/monthly_report.html', context)


@login_required

def monthly_report_pdf(request):
    """Generate monthly report PDF"""
    year, month = _parse_year_month(request)
    job_entries = _get_monthly_report_job_entries(request.user, year, month)
    
    try:
        # Get current user language
        from django.utils.translation import get_language
        language_code = get_language() or getattr(request, 'LANGUAGE_CODE', None) or 'en'
        user_display_name = get_user_display_name(request.user)
        pdf_buffer = generate_monthly_report_pdf(
            job_entries, year, month, user_display_name, language_code
        )
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        filename = f"monthly_report_{request.user.username}_{year}_{month:02d}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, _('Error generating PDF: %(error)s') % {'error': str(e)})
        return redirect('jobs:monthly_report')

