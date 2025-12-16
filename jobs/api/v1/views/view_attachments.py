from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from jobs.models import Attachment
from ..pagination import StandardResultsSetPagination
from ..serializers import AttachmentSerializer


class AttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Attachment model"""
    permission_classes = [IsAuthenticated]
    serializer_class = AttachmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        """Return attachments for user's job entries"""
        return Attachment.objects.filter(
            job_entry__user=self.request.user
        ).select_related('job_entry', 'job_entry__user')
    
    def perform_create(self, serializer):
        """Set file_name and file_type when creating attachment"""
        file = self.request.FILES.get('file')
        if file:
            serializer.save(
                file_name=file.name,
                file_type=file.content_type
            )

