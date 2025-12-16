from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from jobs.models import Notification
from ..pagination import StandardResultsSetPagination
from ..serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_read', 'notification_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return notifications for current user"""
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('user', 'job_entry')
    
    def perform_create(self, serializer):
        """Set user when creating notification"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({'status': 'all marked as read', 'count': count})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})

