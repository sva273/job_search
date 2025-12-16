from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import JobEntry, Category, Tag, ResumeSubmissionStatus
from ..forms import JobEntryForm, ResumeSubmissionStatusForm
from ..pdf_generator import generate_job_pdf
from ..utils import format_history_item, sync_status_from_resume_status, sync_resume_status_from_flags, sync_resume_status_from_general_status


@login_required
def create_job(request):
    """Create a new job entry"""
    if request.method == 'POST':
        form = JobEntryForm(request.POST, user=request.user)
        if form.is_valid():
            job_entry = form.save()
            messages.success(request, _('Job entry saved successfully!'))
            return redirect('jobs:job_detail', job_id=job_entry.id)
    else:
        form = JobEntryForm(user=request.user)
    
    return render(request, 'jobs/create_job.html', {'form': form})


@login_required

def job_list(request):
    """List all user's job entries with advanced search and filters"""
    job_entries = JobEntry.objects.filter(user=request.user).select_related('category').prefetch_related('tags')
    
    # Advanced search
    search_query = request.GET.get('search', '')
    if search_query:
        job_entries = job_entries.filter(
            Q(job_title__icontains=search_query) |
            Q(employer__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(notes__icontains=search_query) |
            Q(contact_email__icontains=search_query) |
            Q(contact_phone__icontains=search_query)
        )
    
    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        job_entries = job_entries.filter(status=status_filter)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        job_entries = job_entries.filter(category_id=category_filter)
    
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        job_entries = job_entries.filter(priority=priority_filter)
    
    work_type_filter = request.GET.get('work_type', '')
    if work_type_filter:
        job_entries = job_entries.filter(work_type=work_type_filter)
    
    source_filter = request.GET.get('source', '')
    if source_filter:
        job_entries = job_entries.filter(source=source_filter)
    
    tag_filter = request.GET.get('tag', '')
    if tag_filter:
        job_entries = job_entries.filter(tags__id=tag_filter)
    
    # Boolean filters
    resume_submitted_filter = request.GET.get('resume_submitted', '')
    if resume_submitted_filter == '1':
        job_entries = job_entries.filter(resume_submitted=True)
    
    response_received_filter = request.GET.get('response_received', '')
    if response_received_filter == '1':
        job_entries = job_entries.filter(response_received=True)
    
    rejection_received_filter = request.GET.get('rejection_received', '')
    if rejection_received_filter == '1':
        job_entries = job_entries.filter(rejection_received=True)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['created_at', '-created_at', 'job_title', '-job_title', 'employer', '-employer', 'priority', '-priority']:
        job_entries = job_entries.order_by(sort_by)
    
    # Get filter options (cached as they rarely change)
    from django.core.cache import cache
    categories = cache.get('all_categories')
    if categories is None:
        categories = list(Category.objects.only('id', 'name', 'color').order_by('name'))
        cache.set('all_categories', categories, 3600)  # Cache for 1 hour
    
    tags = cache.get('all_tags')
    if tags is None:
        tags = list(Tag.objects.only('id', 'name').order_by('name'))
        cache.set('all_tags', tags, 3600)  # Cache for 1 hour
    
    context = {
        'job_entries': job_entries,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'priority_filter': priority_filter,
        'work_type_filter': work_type_filter,
        'source_filter': source_filter,
        'tag_filter': tag_filter,
        'sort_by': sort_by,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'jobs/job_list.html', context)


@login_required

def job_detail(request, job_id):
    """Job entry detail view"""
    job_entry = get_object_or_404(
        JobEntry.objects.select_related('category', 'user').prefetch_related('tags'),
        id=job_id,
        user=request.user
    )
    attachments = job_entry.attachments.only('id', 'file', 'file_name', 'file_type', 'uploaded_at')
    # Get history with limit - show only status changes, last 10 by default, but prepare all for "show all" option
    all_history = job_entry.history.filter(field_name='status').select_related('user').only(
        'id', 'field_name', 'old_value', 'new_value', 'changed_at', 'user__username'
    ).order_by('-changed_at')
    
    history_count = all_history.count()
    history_list = [format_history_item(item) for item in all_history[:10]]
    all_history_list = [format_history_item(item) for item in all_history] if history_count > 10 else history_list
    
    context = {
        'job_entry': job_entry,
        'attachments': attachments,
        'history': history_list,
        'all_history': all_history_list,
        'history_count': history_count,
        'history_has_more': history_count > 10,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required

def edit_job(request, job_id):
    """Edit a job entry"""
    job_entry = get_object_or_404(JobEntry, id=job_id, user=request.user)
    
    if request.method == 'POST':
        # Ensure status is always present in POST data
        post_data = request.POST.copy()
        if 'status' not in post_data or not post_data.get('status'):
            post_data['status'] = job_entry.status or 'not_applied'
        
        form = JobEntryForm(post_data, instance=job_entry, user=request.user)
        if form.is_valid():
            # Get the old values before saving
            old_resume_submitted = job_entry.resume_submitted
            old_application_confirmed = job_entry.application_confirmed
            old_response_received = job_entry.response_received
            old_rejection_received = job_entry.rejection_received
            old_status = job_entry.status
            
            job_entry = form.save()
            
            # Track which fields changed
            changed_fields = []
            if job_entry.resume_submitted != old_resume_submitted:
                changed_fields.append('resume_submitted')
                if job_entry.resume_submitted and not job_entry.resume_submitted_date:
                    job_entry.resume_submitted_date = timezone.now()
            
            if job_entry.application_confirmed != old_application_confirmed:
                changed_fields.append('application_confirmed')
                if job_entry.application_confirmed and not job_entry.confirmation_date:
                    job_entry.confirmation_date = timezone.now()
            
            if job_entry.response_received != old_response_received:
                changed_fields.append('response_received')
                if job_entry.response_received and not job_entry.response_date:
                    job_entry.response_date = timezone.now()
            
            if job_entry.rejection_received != old_rejection_received:
                changed_fields.append('rejection_received')
                if job_entry.rejection_received and not job_entry.rejection_date:
                    job_entry.rejection_date = timezone.now()
            
            # Handle new resume statuses from form FIRST (before auto-status calculation)
            # This ensures that statuses from ResumeSubmissionStatus take priority
            new_status_types = request.POST.getlist('new_status_type')
            new_status_date_times = request.POST.getlist('new_status_date_time')
            new_status_notes = request.POST.getlist('new_status_notes')
            
            # Track if we have new statuses that should determine the main status
            has_new_statuses = bool(new_status_types and any(new_status_types))
            status_updated_from_resume_status = False
            
            for i, status_type in enumerate(new_status_types):
                if status_type and i < len(new_status_date_times) and new_status_date_times[i]:
                    try:
                        from datetime import datetime
                        from django.core.exceptions import ValidationError
                        date_time_str = new_status_date_times[i]
                        # Convert datetime-local format
                        dt = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
                        dt = timezone.make_aware(dt)
                        
                        # Validate that date is not earlier than job entry creation
                        from ..validators import validate_status_date_in_view
                        is_valid, error_msg = validate_status_date_in_view(dt, job_entry)
                        if not is_valid:
                            messages.error(request, error_msg)
                            continue
                        
                        notes = new_status_notes[i] if i < len(new_status_notes) else ''
                        
                        # Create new status
                        status = ResumeSubmissionStatus.objects.create(
                            job_entry=job_entry,
                            status_type=status_type,
                            date_time=dt,
                            notes=notes
                        )
                        
                        # Sync status and flags immediately
                        sync_status_from_resume_status(job_entry, status_type)
                        status_updated_from_resume_status = True
                        
                        # If interview_scheduled, also set interview_date if not set
                        if status_type == 'interview_scheduled' and not job_entry.interview_date:
                            job_entry.interview_date = dt
                    except (ValueError, Exception) as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f'Error creating resume status: {e}', exc_info=True)
            
            # Also sync based on latest existing status if no new ones were added
            latest_existing_status = None
            if not has_new_statuses:
                latest_existing_status = ResumeSubmissionStatus.objects.filter(
                    job_entry=job_entry
                ).order_by('-date_time').first()
                if latest_existing_status:
                    sync_status_from_resume_status(job_entry, latest_existing_status.status_type)
                    status_updated_from_resume_status = True
            
            # Get status from form (may be hidden field with current value)
            form_status = form.cleaned_data.get('status')
            
            # Calculate what the automatic status should be based on flags
            # Note: 'accepted' status cannot be set automatically, only manually
            auto_status = 'not_applied'
            if job_entry.rejection_received:
                auto_status = 'rejected'
            elif job_entry.response_received and not job_entry.rejection_received:
                auto_status = 'response_received'
            elif job_entry.application_confirmed:
                auto_status = 'confirmed'
            elif job_entry.resume_submitted:
                auto_status = 'applied'
            
            # Determine final status - prioritize:
            # 1. Status from ResumeSubmissionStatus (highest priority - user added specific status)
            # 2. User's manual selection from form (if explicitly changed)
            # 3. Current status (if no changes were made to flags that would affect it)
            # 4. Auto-calculated status (only if flags changed and no status was set)
            
            # If status was updated from ResumeSubmissionStatus, keep it (don't override)
            if status_updated_from_resume_status:
                # Status already set by sync_status_from_resume_status, keep it
                # Don't override with auto_status or form_status
                pass
            elif form_status and form_status != old_status:
                # User manually changed status in form, use their choice
                job_entry.status = form_status
                # Create ResumeSubmissionStatus if status changed manually
                sync_resume_status_from_general_status(job_entry, form_status)
            elif changed_fields:
                # Flags were changed, but no new ResumeSubmissionStatus was added
                # Only update status if it makes sense based on the changed flags
                # Don't downgrade status (e.g., if already 'response_received', don't go back to 'applied')
                status_hierarchy = {
                    'not_applied': 0,
                    'applied': 1,
                    'confirmed': 2,
                    'interview_scheduled': 3,
                    'interview_passed': 4,
                    'documents_requested': 4,
                    'response_received': 5,
                    'rejected': 6,
                    'accepted': 7,  # Highest level - can only be set manually
                }
                current_level = status_hierarchy.get(job_entry.status, 0)
                auto_level = status_hierarchy.get(auto_status, 0)
                
                # Only update if auto_status is higher or equal level, or if current status is 'not_applied'
                if auto_level >= current_level or job_entry.status == 'not_applied':
                    job_entry.status = auto_status
                # Otherwise, keep current status (don't downgrade)
            else:
                # No changes to flags, keep current status
                # Only use auto_status if current status is 'not_applied' or empty
                if not job_entry.status or job_entry.status == 'not_applied':
                    job_entry.status = auto_status
            
            # Create ResumeSubmissionStatus for changed flags
            for field in changed_fields:
                sync_resume_status_from_flags(job_entry, field)
            
            # Handle deleted existing statuses
            existing_status_ids = request.POST.getlist('existing_status_ids')
            if existing_status_ids:
                # Delete statuses that are not in the list (user removed them from the page)
                existing_ids = [int(id) for id in existing_status_ids if id and id.isdigit()]
                if existing_ids:
                    ResumeSubmissionStatus.objects.filter(job_entry=job_entry).exclude(id__in=existing_ids).delete()
            
            # Force save to ensure all changes are persisted
            job_entry.save()
            messages.success(request, _('Job entry updated successfully!'))
            return redirect('jobs:job_detail', job_id=job_entry.id)
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = JobEntryForm(instance=job_entry, user=request.user)
    
    # Get resume submission statuses - always fetch fresh data
    # Force evaluation by converting to list to ensure fresh data
    resume_statuses = list(ResumeSubmissionStatus.objects.filter(job_entry=job_entry).order_by('-date_time'))
    
    context = {
        'form': form, 
        'job_entry': job_entry,
        'resume_statuses': resume_statuses
    }
    
    return render(request, 'jobs/edit_job.html', context)


@login_required

def add_resume_status(request, job_id):
    """Add resume submission status"""
    job_entry = get_object_or_404(JobEntry, id=job_id, user=request.user)
    
    if request.method == 'POST':
        # Create a mutable copy of POST data
        post_data = request.POST.copy()
        
        # Handle datetime-local format conversion
        if 'date_time' in post_data:
            date_time_str = post_data['date_time']
            if date_time_str:
                # Convert datetime-local format (YYYY-MM-DDTHH:MM) to Django format
                try:
                    from datetime import datetime
                    dt = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
                    # Make timezone aware
                    from django.utils import timezone
                    dt = timezone.make_aware(dt)
                    post_data['date_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # Try alternative format
                    try:
                        dt = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                        from django.utils import timezone
                        dt = timezone.make_aware(dt)
                        post_data['date_time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass  # Let form handle validation
        
        form = ResumeSubmissionStatusForm(post_data)
        if form.is_valid():
            try:
                status = form.save(commit=False)
                status.job_entry = job_entry
                status.save()
                
                # Синхронизируем общий status и флаги на основе нового ResumeSubmissionStatus
                sync_status_from_resume_status(job_entry, status.status_type)
                job_entry.save()
                
                messages.success(request, _('Resume submission status added successfully!'))
                return redirect('jobs:edit_job', job_id=job_id)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error saving resume status: {e}', exc_info=True)
                messages.error(request, _('Error adding status: %(error)s') % {'error': str(e)})
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('jobs:edit_job', job_id=job_id)


@login_required

def delete_resume_status(request, job_id, status_id):
    """Delete resume submission status"""
    job_entry = get_object_or_404(JobEntry, id=job_id, user=request.user)
    status = get_object_or_404(ResumeSubmissionStatus, id=status_id, job_entry=job_entry)
    
    if request.method == 'POST':
        status.delete()
        messages.success(request, _('Resume submission status deleted successfully!'))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('jobs:edit_job', job_id=job_id)
    
    return redirect('jobs:edit_job', job_id=job_id)


@login_required

def delete_job(request, job_id):
    """Delete a job entry"""
    job_entry = get_object_or_404(JobEntry, id=job_id, user=request.user)
    
    if request.method == 'POST':
        job_entry.delete()
        messages.success(request, _('Job entry deleted!'))
        
        # Support AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        return redirect('jobs:job_list')
    
    return render(request, 'jobs/delete_job.html', {'job_entry': job_entry})


@login_required

def download_job_pdf(request, job_id):
    """Download PDF file with job entry information"""
    job_entry = get_object_or_404(JobEntry, id=job_id, user=request.user)
    
    try:
        # Get current user language
        from django.utils.translation import get_language
        language_code = get_language() or 'ru'
        # Note: generate_job_pdf doesn't use username, but we keep it for consistency
        pdf_buffer = generate_job_pdf(job_entry, language_code)
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        filename = f"vacancy_{job_entry.id}_{job_entry.job_title[:50]}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, _('Error generating PDF: %(error)s') % {'error': str(e)})
        return redirect('jobs:job_detail', job_id=job_id)

