from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import JobEntry, JobEntryHistory, Notification, Category, Tag
from django.utils import timezone



@receiver(pre_save, sender=JobEntry)
def track_job_entry_changes(sender, instance, **kwargs):
    """Track changes to job entry fields"""
    if instance.pk:
        try:
            old_instance = JobEntry.objects.select_related('user').get(pk=instance.pk)
            user = instance.user
            
            # List of fields to track
            tracked_fields = [
                'status', 'job_title', 'employer', 'priority', 'category',
                'resume_submitted', 'application_confirmed', 'response_received',
                'rejection_received', 'interview_date', 'follow_up_date',
                'application_deadline'
            ]
            
            # Collect all changes first, then bulk create
            history_entries = []
            for field in tracked_fields:
                old_value = getattr(old_instance, field, None)
                new_value = getattr(instance, field, None)
                
                # Convert to string for comparison
                if old_value != new_value:
                    old_str = str(old_value) if old_value is not None else ''
                    new_str = str(new_value) if new_value is not None else ''
                    
                    history_entries.append(
                        JobEntryHistory(
                            job_entry=instance,
                            user=user,
                            field_name=field,
                            old_value=old_str,
                            new_value=new_str
                        )
                    )
            
            # Bulk create all history entries at once
            if history_entries:
                JobEntryHistory.objects.bulk_create(history_entries)
        except JobEntry.DoesNotExist:
            pass


@receiver(post_save, sender=JobEntry)
def create_notifications(sender, instance, created, **kwargs):
    """Create notifications for important dates only"""
    user = instance.user
    
    # Invalidate notifications count cache
    cache.delete(f'notifications_count_{user.id}')
    
    # Store notification text as template strings that will be translated in views/templates
    # Use English as base language for storage, translation happens at display time
    
    # Notification for upcoming interview
    # Store English text in database, translation happens in views.py
    if instance.interview_date and instance.interview_date > timezone.now():
        title = 'Upcoming interview: %(job_title)s' % {'job_title': instance.job_title}
        message = 'Interview scheduled for %(date)s' % {
            'date': instance.interview_date.strftime("%Y-%m-%d %H:%M")
        }
        Notification.objects.get_or_create(
            user=user,
            job_entry=instance,
            notification_type='interview',
            defaults={
                'title': title,
                'message': message,
            }
        )
    
    # Notification for follow-up reminder
    if instance.follow_up_date and instance.follow_up_date > timezone.now():
        title = 'Follow-up reminder: %(job_title)s' % {'job_title': instance.job_title}
        message = 'Follow-up scheduled for %(date)s' % {
            'date': instance.follow_up_date.strftime("%Y-%m-%d %H:%M")
        }
        Notification.objects.get_or_create(
            user=user,
            job_entry=instance,
            notification_type='followup',
            defaults={
                'title': title,
                'message': message,
            }
        )
    
    # Notification for application deadline
    if instance.application_deadline and instance.application_deadline >= timezone.now().date():
        title = 'Application deadline: %(job_title)s' % {'job_title': instance.job_title}
        message = 'Application deadline: %(date)s' % {
            'date': instance.application_deadline.strftime("%Y-%m-%d")
        }
        Notification.objects.get_or_create(
            user=user,
            job_entry=instance,
            notification_type='deadline',
            defaults={
                'title': title,
                'message': message,
            }
        )


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_categories_cache(sender, **kwargs):
    """Invalidate categories cache when Category is created/updated/deleted"""
    cache.delete('all_categories')


@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
def invalidate_tags_cache(sender, **kwargs):
    """Invalidate tags cache when Tag is created/updated/deleted"""
    cache.delete('all_tags')

