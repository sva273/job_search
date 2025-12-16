from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login, authenticate
from ..models import JobEntry
from ..forms import UserRegistrationForm


def register(request):
    """Register a new user"""
    if request.user.is_authenticated:
        return redirect('jobs:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, _('Welcome, %(username)s!') % {'username': username})
                return redirect('jobs:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'jobs/register.html', {'form': form})


@login_required
def dashboard(request):
    """User dashboard"""
    user_jobs = JobEntry.objects.filter(user=request.user)
    job_entries = user_jobs.select_related('category').prefetch_related('tags').only(
        'id', 'job_title', 'employer', 'status', 'created_at', 
        'category__name', 'category__color'
    )[:5]
    
    context = {
        'job_entries': job_entries,
        'jobs_count': user_jobs.count(),
    }
    return render(request, 'jobs/dashboard.html', context)

