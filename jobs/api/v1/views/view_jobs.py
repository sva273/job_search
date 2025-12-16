from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from jobs.models import JobEntry, ResumeSubmissionStatus, JobEntryHistory
from ..pagination import StandardResultsSetPagination
from ..serializers import (
    JobEntrySerializer, JobEntryListSerializer,
    ResumeSubmissionStatusSerializer, JobEntryHistorySerializer,
    AttachmentSerializer
)


class JobEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for JobEntry model
    
    list: Get list of user's job entries
    retrieve: Get job entry details
    create: Create new job entry
    update: Update job entry
    partial_update: Partially update job entry
    destroy: Delete job entry
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'work_type', 'source', 'category']
    search_fields = [
        'job_title', 'employer', 'description', 'address',
        'notes', 'contact_email', 'contact_phone'
    ]
    ordering_fields = ['created_at', 'updated_at', 'job_title', 'employer', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return job entries for current user"""
        queryset = JobEntry.objects.filter(
            user=self.request.user
        ).select_related('category', 'user').prefetch_related('tags', 'resume_statuses')
        
        # Additional filtering
        tag_filter = self.request.query_params.get('tag', None)
        if tag_filter:
            queryset = queryset.filter(tags__id=tag_filter)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return JobEntryListSerializer
        return JobEntrySerializer
    
    
    def perform_create(self, serializer):
        """Set user when creating job entry"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get history for a job entry"""
        job_entry = self.get_object()
        history = job_entry.history.select_related('user').all()[:20]
        serializer = JobEntryHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attachments(self, request, pk=None):
        """Get attachments for a job entry"""
        job_entry = self.get_object()
        attachments = job_entry.attachments.all()
        serializer = AttachmentSerializer(attachments, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def resume_statuses(self, request, pk=None):
        """Get or create resume submission statuses for a job entry"""
        job_entry = self.get_object()
        if request.method == 'GET':
            statuses = job_entry.resume_statuses.all()
            serializer = ResumeSubmissionStatusSerializer(statuses, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = ResumeSubmissionStatusSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(job_entry=job_entry)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResumeSubmissionStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for ResumeSubmissionStatus model"""
    permission_classes = [IsAuthenticated]
    serializer_class = ResumeSubmissionStatusSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_time', 'created_at']
    ordering = ['-date_time']
    
    def get_queryset(self):
        """Return resume statuses for user's job entries"""
        return ResumeSubmissionStatus.objects.filter(
            job_entry__user=self.request.user
        ).select_related('job_entry', 'job_entry__user')
    
    def perform_create(self, serializer):
        """Verify job_entry belongs to user"""
        job_entry = serializer.validated_data['job_entry']
        if job_entry.user != self.request.user:
            raise serializers.ValidationError("Job entry does not belong to user")
        serializer.save()


class JobEntryHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for JobEntryHistory model (read-only)"""
    permission_classes = [IsAuthenticated]
    serializer_class = JobEntryHistorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['changed_at']
    ordering = ['-changed_at']
    
    def get_queryset(self):
        """Return history for user's job entries"""
        return JobEntryHistory.objects.filter(
            job_entry__user=self.request.user
        ).select_related('user', 'job_entry', 'job_entry__user')

