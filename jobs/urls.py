from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Create your models here.
app_name = 'jobs'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='jobs/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Home and dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Job entries
    path('jobs/create/', views.create_job, name='create_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('jobs/<int:job_id>/pdf/', views.download_job_pdf, name='download_job_pdf'),
    path('jobs/<int:job_id>/resume-status/add/', views.add_resume_status, name='add_resume_status'),
    path('jobs/<int:job_id>/resume-status/<int:status_id>/delete/', views.delete_resume_status,
         name='delete_resume_status'),
    
    # Statistics
    path('statistics/', views.statistics, name='statistics'),
    path('statistics/pdf/', views.download_statistics_pdf, name='download_statistics_pdf'),
    path('statistics/monthly-report/', views.monthly_report, name='monthly_report'),
    path('statistics/monthly-report/pdf/', views.monthly_report_pdf, name='monthly_report_pdf'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    
    # Templates
    path('templates/', views.job_templates, name='job_templates'),
    path('templates/<int:template_id>/create/', views.create_from_template, name='create_from_template'),
    path('templates/<int:template_id>/edit/', views.edit_template, name='edit_template'),
    path('templates/<int:template_id>/delete/', views.delete_template, name='delete_template'),
    
    # Attachments
    path('jobs/<int:job_id>/attachments/upload/', views.upload_attachment, name='upload_attachment'),
    path('attachments/<int:attachment_id>/delete/', views.delete_attachment, name='delete_attachment'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    
    # Theme
    path('theme/toggle/', views.toggle_theme, name='toggle_theme'),
    
    # Profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Categories
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    
    # Tags
    path('tags/', views.tags_list, name='tags_list'),
    path('tags/create/', views.create_tag, name='create_tag'),
    path('tags/<int:tag_id>/edit/', views.edit_tag, name='edit_tag'),
    path('tags/<int:tag_id>/delete/', views.delete_tag, name='delete_tag'),
]

