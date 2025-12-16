from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import activate, gettext as _
from django.conf import settings
from datetime import timedelta
from jobs.models import JobEntry, UserProfile


class Command(BaseCommand):
    help = 'Send email reminders for upcoming interviews, follow-ups, and deadlines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days before event to send reminder (default: 1)',
        )

    def handle(self, *args, **options):
        days_before = options['days']
        now = timezone.now()
        reminder_date = now + timedelta(days=days_before)
        
        # Get all users with email notifications enabled
        users_with_notifications = UserProfile.objects.filter(
            email_notifications_enabled=True
        ).select_related('user')
        
        emails_sent = 0
        
        for profile in users_with_notifications:
            user = profile.user
            if not user.email:
                continue
            
            # Activate user's language preference (if available)
            # For now, use default language
            activate(settings.LANGUAGE_CODE)
            
            user_jobs = JobEntry.objects.filter(user=user)
            
            # Get upcoming interviews
            interviews = user_jobs.filter(
                interview_date__gte=now,
                interview_date__lte=reminder_date
            ).exclude(interview_date__isnull=True)
            
            # Get upcoming follow-ups
            follow_ups = user_jobs.filter(
                follow_up_date__gte=now,
                follow_up_date__lte=reminder_date
            ).exclude(follow_up_date__isnull=True)
            
            # Get upcoming deadlines
            deadlines = user_jobs.filter(
                application_deadline__gte=now.date(),
                application_deadline__lte=reminder_date.date()
            ).exclude(application_deadline__isnull=True)
            
            if interviews.exists() or follow_ups.exists() or deadlines.exists():
                subject = _('Job Search Reminders')
                message_parts = []
                
                if interviews.exists():
                    message_parts.append(_('Upcoming Interviews:'))
                    for job in interviews:
                        message_parts.append(
                            f"- {job.job_title} at {job.employer} on {job.interview_date.strftime('%d.%m.%Y %H:%M')}"
                        )
                    message_parts.append('')
                
                if follow_ups.exists():
                    message_parts.append(_('Follow-ups:'))
                    for job in follow_ups:
                        message_parts.append(
                            f"- {job.job_title} at {job.employer} on {job.follow_up_date.strftime('%d.%m.%Y %H:%M')}"
                        )
                    message_parts.append('')
                
                if deadlines.exists():
                    message_parts.append(_('Application Deadlines:'))
                    for job in deadlines:
                        message_parts.append(
                            f"- {job.job_title} at {job.employer} on {job.application_deadline.strftime('%d.%m.%Y')}"
                        )
                    message_parts.append('')
                
                message = '\n'.join(message_parts)
                message += _('Visit your calendar to see all events:') + f' {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "localhost:8000"}/calendar/'
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    emails_sent += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Sent reminder email to {user.email}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send email to {user.email}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {emails_sent} reminder email(s)')
        )

