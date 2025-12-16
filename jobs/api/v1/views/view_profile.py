from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from jobs.models import UserProfile
from ..serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        """Return profile for current user"""
        return UserProfile.objects.filter(user=self.request.user).select_related('user')
    
    def get_object(self):
        """Get or create profile for current user"""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def perform_create(self, serializer):
        """Set user when creating profile"""
        serializer.save(user=self.request.user)

