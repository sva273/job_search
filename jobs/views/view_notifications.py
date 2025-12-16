from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ..models import Notification

def notifications(request):
    """User notifications"""
    from django.utils.translation import gettext as translation_gettext, get_language, activate
    
    # Get and activate current language
    current_language = get_language() or getattr(request, 'LANGUAGE_CODE', None) or 'en'
    activate(current_language)
    
    notifications_list = Notification.objects.filter(user=request.user).select_related(
        'job_entry'
    ).only(
        'id', 'title', 'message', 'notification_type', 'is_read', 
        'created_at', 'job_entry__id', 'job_entry__job_title'
    ).order_by('-created_at')
    unread_count = notifications_list.filter(is_read=False).count()
    
    # Translation patterns
    title_patterns = {
        'Upcoming interview: ': lambda title: translation_gettext('Upcoming interview: %(job_title)s') % {
            'job_title': title.replace('Upcoming interview: ', '')
        },
        'Follow-up reminder: ': lambda title: translation_gettext('Follow-up reminder: %(job_title)s') % {
            'job_title': title.replace('Follow-up reminder: ', '')
        },
        'Application deadline: ': lambda title: translation_gettext('Application deadline: %(job_title)s') % {
            'job_title': title.replace('Application deadline: ', '')
        },
    }
    
    message_patterns = {
        'Interview scheduled for ': lambda msg: translation_gettext('Interview scheduled for %(date)s') % {
            'date': msg.replace('Interview scheduled for ', '')
        },
        'Follow-up scheduled for ': lambda msg: translation_gettext('Follow-up scheduled for %(date)s') % {
            'date': msg.replace('Follow-up scheduled for ', '')
        },
        'Application deadline: ': lambda msg: translation_gettext('Application deadline: %(date)s') % {
            'date': msg.replace('Application deadline: ', '')
        },
    }
    
    # Translate notification titles and messages
    for notification in notifications_list:
        # Translate title
        translated_title = None
        for pattern, translate_func in title_patterns.items():
            if notification.title.startswith(pattern):
                translated_title = translate_func(notification.title)
                break
        notification.translated_title = translated_title or translation_gettext(notification.title)
        
        # Translate message
        translated_message = None
        for pattern, translate_func in message_patterns.items():
            if notification.message.startswith(pattern):
                translated_message = translate_func(notification.message)
                break
        notification.translated_message = translated_message or translation_gettext(notification.message)
    
    # Mark as read if viewing
    if request.GET.get('mark_read'):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        # Invalidate cache
        from django.core.cache import cache
        cache.delete(f'notifications_count_{request.user.id}')
        
        # Return JSON response for AJAX requests or redirect for regular requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            return JsonResponse({'success': True, 'unread_count': unread_count})
        
        messages.success(request, _('All notifications marked as read!'))
        return redirect('jobs:notifications')
    
    context = {
        'notifications': notifications_list,
        'unread_count': unread_count,
    }
    return render(request, 'jobs/notifications.html', context)


@login_required

def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Invalidate cache
    from django.core.cache import cache
    cache.delete(f'notifications_count_{request.user.id}')
    
    # Return JSON response for AJAX requests or redirect for regular requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'success': True, 'unread_count': unread_count})
    return redirect('jobs:notifications')


@login_required

def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if request.method == 'POST':
        notification.delete()
        # Invalidate cache
        from django.core.cache import cache
        cache.delete(f'notifications_count_{request.user.id}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            return JsonResponse({'success': True, 'unread_count': unread_count})
        else:
            messages.success(request, _('Notification deleted successfully!'))
            return redirect('jobs:notifications')
    
    return redirect('jobs:notifications')


@login_required

def delete_all_notifications(request):
    """Delete all notifications for the user"""
    if request.method == 'POST':
        deleted_count = Notification.objects.filter(user=request.user).delete()[0]
        # Invalidate cache
        from django.core.cache import cache
        cache.delete(f'notifications_count_{request.user.id}')
        
        messages.success(request, _('%(count)s notification(s) deleted successfully!') % {'count': deleted_count})
        return redirect('jobs:notifications')
    
    return redirect('jobs:notifications')

