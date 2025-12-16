from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import UserProfile
from ..forms import UserProfileForm

def toggle_theme(request):
    """Toggle user theme preference"""
    if request.method == 'POST':
        theme = request.POST.get('theme', 'light')
        if theme in ['light', 'dark', 'auto']:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.theme = theme
            profile.save()
            messages.success(request, _('Theme updated successfully!'))
        return redirect(request.META.get('HTTP_REFERER', 'jobs:dashboard'))
    return redirect('jobs:dashboard')


@login_required

def edit_profile(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'theme': 'light', 'email_notifications_enabled': True, 'reminder_days_before': 3}
    )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Update User model fields directly
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save(update_fields=['first_name', 'last_name'])
            messages.success(request, _('Profile updated successfully!'))
            return redirect('jobs:edit_profile')
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })
    
    return render(request, 'jobs/edit_profile.html', {'form': form})

