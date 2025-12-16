from rest_framework import serializers
from django.contrib.auth.models import User
from jobs.models import (
    JobEntry, Category, Tag, JobTemplate, 
    Attachment, Notification, JobEntryHistory, UserProfile,
    ResumeSubmissionStatus
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']


class ResumeSubmissionStatusSerializer(serializers.ModelSerializer):
    """Serializer for ResumeSubmissionStatus model"""
    job_entry_id = serializers.PrimaryKeyRelatedField(
        queryset=JobEntry.objects.all(),
        source='job_entry',
        write_only=True
    )
    status_type_display = serializers.CharField(source='get_status_type_display', read_only=True)
    
    class Meta:
        model = ResumeSubmissionStatus
        fields = [
            'id', 'job_entry_id', 'status_type', 'status_type_display',
            'date_time', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class JobEntrySerializer(serializers.ModelSerializer):
    """Serializer for JobEntry model"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source='tags',
        write_only=True,
        required=False
    )
    resume_statuses = ResumeSubmissionStatusSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = JobEntry
        fields = [
            'id', 'user', 'job_title', 'employer', 'address',
            'contact_email', 'contact_phone', 'company_website', 'job_url',
            'description', 'category', 'category_id', 'tags', 'tag_ids',
            'salary_min', 'salary_max', 'salary_currency', 'work_type',
            'priority', 'source', 'interview_date', 'follow_up_date',
            'application_deadline', 'reminder_sent', 'resume_submitted',
            'resume_submitted_date', 'application_confirmed', 'confirmation_date',
            'response_received', 'response_date', 'rejection_received',
            'rejection_date', 'status', 'notes', 'resume_statuses',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class JobEntryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for JobEntry list view"""
    category = serializers.StringRelatedField()
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = JobEntry
        fields = [
            'id', 'job_title', 'employer', 'category', 'tags',
            'status', 'priority', 'work_type', 'created_at'
        ]


class JobTemplateSerializer(serializers.ModelSerializer):
    """Serializer for JobTemplate model"""
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = JobTemplate
        fields = [
            'id', 'user', 'name', 'job_title', 'employer',
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Attachment model"""
    job_entry_id = serializers.PrimaryKeyRelatedField(
        queryset=JobEntry.objects.all(),
        source='job_entry',
        write_only=True
    )
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'job_entry_id', 'file', 'file_url', 'file_name',
            'file_type', 'description', 'uploaded_at'
        ]
        read_only_fields = ['id', 'file_name', 'file_type', 'uploaded_at']
    
    def get_file_url(self, obj):
        """Return full URL for file"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    user = serializers.ReadOnlyField(source='user.username')
    job_entry_id = serializers.PrimaryKeyRelatedField(
        queryset=JobEntry.objects.all(),
        source='job_entry',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'job_entry_id', 'title', 'message',
            'notification_type', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class JobEntryHistorySerializer(serializers.ModelSerializer):
    """Serializer for JobEntryHistory model"""
    user = serializers.ReadOnlyField(source='user.username')
    job_entry_id = serializers.PrimaryKeyRelatedField(
        queryset=JobEntry.objects.all(),
        source='job_entry',
        write_only=True
    )
    
    class Meta:
        model = JobEntryHistory
        fields = [
            'id', 'job_entry_id', 'user', 'field_name',
            'old_value', 'new_value', 'changed_at'
        ]
        read_only_fields = ['id', 'user', 'changed_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'theme', 'email_notifications_enabled',
            'reminder_days_before', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']

