from django.core.cache import cache
from .models import Notification, UserProfile


def notifications_count(request):
    """Add unread notifications count to template context"""
    if request.user.is_authenticated:
        # Cache for 5 minutes to reduce database queries
        cache_key = f'notifications_count_{request.user.id}'
        unread_count = cache.get(cache_key)
        if unread_count is None:
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            cache.set(cache_key, unread_count, 300)  # 5 minutes
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}


def user_theme(request):
    """Context processor to add user theme preference to all templates"""
    theme = 'light'
    if request.user.is_authenticated:
        # Use get_or_create to avoid exception handling and ensure profile exists
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'theme': 'light'}
        )
        theme = profile.theme
        # If auto, detect system preference
        if theme == 'auto':
            # Check if user prefers dark mode (via cookie or header)
            prefers_dark = request.COOKIES.get('prefers-color-scheme') == 'dark'
            theme = 'dark' if prefers_dark else 'light'
    
    return {
        'user_theme': theme
    }

