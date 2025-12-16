from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from jobs.models import Category, Tag, JobTemplate
from ..pagination import StandardResultsSetPagination
from ..serializers import (
    CategorySerializer, TagSerializer, JobTemplateSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Category model (read-only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Tag model (read-only)"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class JobTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for JobTemplate model"""
    permission_classes = [IsAuthenticated]
    serializer_class = JobTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'job_title', 'employer', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Return templates for current user"""
        return JobTemplate.objects.filter(user=self.request.user).select_related('user')
    
    def perform_create(self, serializer):
        """Set user when creating template"""
        serializer.save(user=self.request.user)

