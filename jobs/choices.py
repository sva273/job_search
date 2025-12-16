from django.utils.translation import gettext_lazy as _


STATUS_CHOICES = [
    ('not_applied', _('Not Applied')),
    ('applied', _('Applied')),
    ('confirmed', _('Application Confirmed')),
    ('interview_scheduled', _('Interview Scheduled')),
    ('interview_passed', _('Interview Passed')),
    ('documents_requested', _('Documents Requested')),
    ('response_received', _('Response Received')),
    ('rejected', _('Rejected')),
    ('accepted', _('Accepted')),
]


PRIORITY_CHOICES = [
    ('high', _('High')),
    ('medium', _('Medium')),
    ('low', _('Low')),
]


WORK_TYPE_CHOICES = [
    ('remote', _('Remote')),
    ('office', _('Office')),
    ('home_office', _('Home Office')),
    ('hybrid', _('Hybrid')),
    ('flexible', _('Flexible')),
]


SOURCE_CHOICES = [
    ('linkedin', _('LinkedIn')),
    ('indeed', _('Indeed')),
    ('stepstone', _('StepStone')),
    ('xing', _('XING')),
    ('employment_agency', _('Employment Agency')),
    ('jobcenter', _('Jobcenter')),
    ('company_website', _('Company Website')),
    ('recruiter', _('Recruiter')),
    ('referral', _('Referral')),
    ('other', _('Other')),
]

RESUME_SUBMISSION_STATUS_CHOICES = [
    ('resume_sent', _('Resume Sent')),
    ('confirmation_received', _('Confirmation of Receipt Received')),
    ('interview_scheduled', _('Interview Scheduled')),
    ('interview_passed', _('Interview Passed')),
    ('another_interview_scheduled', _('Another Interview Scheduled')),
    ('documents_requested', _('Additional Documents Requested')),
    ('rejection_received', _('Rejection Received')),
]

