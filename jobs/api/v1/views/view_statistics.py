from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from jobs.models import JobEntry
from ..serializers import JobEntryListSerializer


class StatisticsView(APIView):
    """API endpoint for job statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get statistics for user's job entries"""
        from jobs.utils import get_statistics_data
        
        user_jobs = JobEntry.objects.filter(user=request.user).select_related('category')
        statistics_data = get_statistics_data(user_jobs)
        
        return Response(statistics_data)


class MonthlyReportView(APIView):
    """API endpoint for monthly report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get monthly report for user's job entries"""
        from jobs.views.view_statistics import _get_monthly_report_job_entries
        from jobs.views.view_statistics import _parse_year_month
        
        year_month = request.query_params.get('month', None)
        if not year_month:
            # Default to current month
            now = timezone.now()
            year_month = f"{now.year}-{now.month:02d}"
        
        year, month = _parse_year_month(year_month)
        job_entries = _get_monthly_report_job_entries(request.user, year, month)
        
        serializer = JobEntryListSerializer(job_entries, many=True)
        return Response({
            'year': year,
            'month': month,
            'total_entries': len(job_entries),
            'job_entries': serializer.data
        })


class CalendarView(APIView):
    """API endpoint for calendar events"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get calendar events for user's job entries"""
        start_date = request.query_params.get('start', None)
        end_date = request.query_params.get('end', None)
        
        if start_date:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end_date = start_date + timedelta(days=30)
        
        events = []
        job_entries = JobEntry.objects.filter(
            user=request.user
        ).filter(
            Q(interview_date__range=[start_date, end_date]) |
            Q(follow_up_date__range=[start_date, end_date]) |
            Q(application_deadline__range=[start_date.date(), end_date.date()])
        ).select_related('category')
        
        for job in job_entries:
            if job.interview_date and start_date <= job.interview_date <= end_date:
                events.append({
                    'id': f'interview_{job.id}',
                    'title': f"Interview: {job.job_title} - {job.employer}",
                    'start': job.interview_date.isoformat(),
                    'end': (job.interview_date + timedelta(hours=1)).isoformat(),
                    'type': 'interview',
                    'job_id': job.id,
                    'color': '#28a745'
                })
            
            if job.follow_up_date and start_date <= job.follow_up_date <= end_date:
                events.append({
                    'id': f'followup_{job.id}',
                    'title': f"Follow-up: {job.job_title} - {job.employer}",
                    'start': job.follow_up_date.isoformat(),
                    'end': (job.follow_up_date + timedelta(hours=1)).isoformat(),
                    'type': 'follow_up',
                    'job_id': job.id,
                    'color': '#17a2b8'
                })
            
            if job.application_deadline:
                deadline_start = timezone.make_aware(
                    datetime.combine(job.application_deadline, datetime.min.time())
                )
                if start_date <= deadline_start <= end_date:
                    events.append({
                        'id': f'deadline_{job.id}',
                        'title': f"Deadline: {job.job_title} - {job.employer}",
                        'start': deadline_start.isoformat(),
                        'end': (deadline_start + timedelta(hours=1)).isoformat(),
                        'type': 'deadline',
                        'job_id': job.id,
                        'color': '#dc3545'
                    })
        
        return Response(events)

