from django.contrib import admin
from .models import JobEntry, Category, Tag, JobTemplate, JobEntryHistory, Attachment, Notification, UserProfile

# Create your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(JobTemplate)
class JobTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'updated_at')
    list_filter = ('user', 'updated_at')
    search_fields = ('name', 'job_title', 'employer')


@admin.register(JobEntry)
class JobEntryAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'employer', 'user', 'status', 'priority', 'category', 'resume_submitted', 'created_at')
    list_filter = ('status', 'priority', 'category', 'work_type', 'source', 'resume_submitted', 'application_confirmed',
                   'response_received', 'rejection_received', 'created_at', 'employer')
    search_fields = ('job_title', 'employer', 'user__username', 'notes', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'job_title', 'employer', 'address', 'job_url', 'description')
        }),
        ('Categories and Tags', {
            'fields': ('category', 'tags')
        }),
        ('Additional Information', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'work_type', 'priority', 'source')
        }),
        ('Calendar', {
            'fields': ('interview_date', 'follow_up_date', 'application_deadline', 'reminder_sent')
        }),
        ('Contacts', {
            'fields': ('contact_email', 'contact_phone', 'company_website')
        }),
        ('Application Status', {
            'fields': ('status', 'resume_submitted', 'resume_submitted_date', 
                      'application_confirmed', 'confirmation_date',
                      'response_received', 'response_date',
                      'rejection_received', 'rejection_date', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(JobEntryHistory)
class JobEntryHistoryAdmin(admin.ModelAdmin):
    list_display = ('job_entry', 'field_name', 'user', 'changed_at')
    list_filter = ('field_name', 'changed_at')
    search_fields = ('job_entry__job_title', 'field_name', 'old_value', 'new_value')
    readonly_fields = ('changed_at',)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'job_entry', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('file_name', 'description', 'job_entry__job_title')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'job_entry', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'email_notifications_enabled', 'reminder_days_before', 'updated_at')
    list_filter = ('theme', 'email_notifications_enabled', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

