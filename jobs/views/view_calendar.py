from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import JobEntry

def calendar_view(request):
    """Calendar view with interviews, follow-ups, and deadlines"""
    user_jobs = JobEntry.objects.filter(user=request.user).select_related('category').only(
        'id', 'job_title', 'employer', 'interview_date', 'follow_up_date', 
        'application_deadline', 'category__name', 'category__color'
    )
    
    # Get all events (not just upcoming) for calendar display
    now = timezone.now()
    today = now.date()
    
    # Optimize queries by using single queryset with conditional filtering
    interviews = user_jobs.exclude(interview_date__isnull=True).order_by('interview_date')
    follow_ups = user_jobs.exclude(follow_up_date__isnull=True).order_by('follow_up_date')
    deadlines = user_jobs.exclude(application_deadline__isnull=True).order_by('application_deadline')
    
    # Also get upcoming for the list view (evaluate querysets only when needed)
    upcoming_interviews = interviews.filter(interview_date__gte=now)
    upcoming_follow_ups = follow_ups.filter(follow_up_date__gte=now)
    upcoming_deadlines = deadlines.filter(application_deadline__gte=today)
    
    context = {
        'interviews': upcoming_interviews,
        'follow_ups': upcoming_follow_ups,
        'deadlines': upcoming_deadlines,
        # For calendar
        'all_interviews': interviews,
        'all_follow_ups': follow_ups,
        'all_deadlines': deadlines,
    }
    return render(request, 'jobs/calendar.html', context)

