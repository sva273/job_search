from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import JobEntry, Tag, ResumeSubmissionStatus
from ..choices import RESUME_SUBMISSION_STATUS_CHOICES


class JobEntryForm(forms.ModelForm):
    """Form for creating/editing job entries"""
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label=_('Tags')
    )
    
    class Meta:
        model = JobEntry
        fields = (
            'job_title', 'employer', 'address', 
            'contact_email', 'contact_phone', 
            'company_website', 'job_url', 'description',
            'category', 'tags',
            'salary_min', 'salary_max', 'salary_currency',
            'work_type', 'priority', 'source',
            'interview_date', 'follow_up_date', 'application_deadline',
            'resume_submitted', 'resume_submitted_date',
            'application_confirmed', 'confirmation_date',
            'response_received', 'response_date',
            'rejection_received', 'rejection_date',
            'status', 'notes'
        )
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'employer': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control'}),
            'job_url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_currency': forms.Select(attrs={'class': 'form-control'}),
            'work_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'interview_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'follow_up_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resume_submitted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'resume_submitted_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'application_confirmed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'confirmation_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'response_received': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'response_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'rejection_received': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rejection_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Set currency choices and make it not required
        self.fields['salary_currency'].required = False
        self.fields['salary_currency'].widget = forms.Select(choices=[
            ('', '---------'), ('USD', 'USD'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('RUB', 'RUB'), ('CHF', 'CHF')
        ], attrs={'class': 'form-control'})
        # Make fields not required
        self.fields['priority'].required = False
        self.fields['work_type'].required = False
        self.fields['source'].required = False
        self.fields['salary_min'].required = False
        self.fields['salary_max'].required = False
        # Add empty choice to select fields
        if self.fields['work_type'].choices:
            self.fields['work_type'].choices = [('', '---------')] + list(self.fields['work_type'].choices)
        if self.fields['priority'].choices:
            self.fields['priority'].choices = [('', '---------')] + list(self.fields['priority'].choices)
        if self.fields['source'].choices:
            self.fields['source'].choices = [('', '---------')] + list(self.fields['source'].choices)
        # Set tags queryset to all tags (tags are global, not user-specific)
        self.fields['tags'].queryset = Tag.objects.all()
        
        # Hide status fields when creating a new job entry
        if not self.instance.pk:
            self.fields['resume_submitted'].widget = forms.HiddenInput()
            self.fields['resume_submitted_date'].widget = forms.HiddenInput()
            self.fields['application_confirmed'].widget = forms.HiddenInput()
            self.fields['confirmation_date'].widget = forms.HiddenInput()
            self.fields['response_received'].widget = forms.HiddenInput()
            self.fields['response_date'].widget = forms.HiddenInput()
            self.fields['rejection_received'].widget = forms.HiddenInput()
            self.fields['rejection_date'].widget = forms.HiddenInput()
            self.fields['status'].widget = forms.HiddenInput()
            self.fields['notes'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        # Handle checkboxes - Django doesn't send unchecked checkboxes in POST
        # So we need to explicitly set them to False if not present
        checkbox_fields = ['resume_submitted', 'application_confirmed', 'response_received', 'rejection_received']
        for field in checkbox_fields:
            cleaned_data[field] = field in self.data
        
        # Set default values for fields that might be hidden or not provided
        defaults = {
            'salary_currency': 'USD',
            'priority': 'medium',
        }
        for field, default_value in defaults.items():
            if field not in cleaned_data or not cleaned_data.get(field):
                cleaned_data[field] = default_value
            
        return cleaned_data
    
    def save(self, commit=True):
        job_entry = super().save(commit=False)
        if self.user:
            job_entry.user = self.user
        
        # Explicitly set boolean fields from cleaned_data (always present after clean())
        job_entry.resume_submitted = self.cleaned_data.get('resume_submitted', False)
        job_entry.application_confirmed = self.cleaned_data.get('application_confirmed', False)
        job_entry.response_received = self.cleaned_data.get('response_received', False)
        job_entry.rejection_received = self.cleaned_data.get('rejection_received', False)
        
        # Set default values for required fields if not provided
        if not job_entry.salary_currency:
            job_entry.salary_currency = 'USD'
        if not job_entry.priority:
            job_entry.priority = 'medium'
        
        if commit:
            job_entry.save()
            # Save many-to-many fields
            self.save_m2m()
        return job_entry


class ResumeSubmissionStatusForm(forms.ModelForm):
    """Form for adding resume submission status"""
    class Meta:
        model = ResumeSubmissionStatus
        fields = ['status_type', 'date_time', 'notes']
        widgets = {
            'status_type': forms.Select(attrs={'class': 'form-control'}),
            'date_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Optional notes')}),
        }
        labels = {
            'status_type': _('Status Type'),
            'date_time': _('Date and Time'),
            'notes': _('Notes'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status_type'].choices = [('', '---------')] + list(RESUME_SUBMISSION_STATUS_CHOICES)
        # Set input format for datetime-local
        self.fields['date_time'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
    
    def clean_date_time(self):
        """Clean and convert datetime-local format"""
        date_time = self.cleaned_data.get('date_time')
        if date_time:
            # If it's a string, try to parse it
            if isinstance(date_time, str):
                from django.utils.dateparse import parse_datetime
                parsed = parse_datetime(date_time)
                if parsed:
                    return parsed
        return date_time

