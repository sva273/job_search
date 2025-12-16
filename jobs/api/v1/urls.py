from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobEntryViewSet, ResumeSubmissionStatusViewSet, JobEntryHistoryViewSet,
    CategoryViewSet, TagViewSet, JobTemplateViewSet,
    AttachmentViewSet, NotificationViewSet, UserProfileViewSet,
    StatisticsView, MonthlyReportView, CalendarView
)

app_name = 'api_v1'

router = DefaultRouter()
router.register(r'jobs', JobEntryViewSet, basename='job')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'templates', JobTemplateViewSet, basename='template')
router.register(r'attachments', AttachmentViewSet, basename='attachment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'history', JobEntryHistoryViewSet, basename='history')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'resume-status', ResumeSubmissionStatusViewSet, basename='resume-status')

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('monthly-report/', MonthlyReportView.as_view(), name='monthly-report'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
]

