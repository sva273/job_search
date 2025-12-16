from django import forms
from ..models import JobTemplate


class JobTemplateForm(forms.ModelForm):
    """Form for creating/editing job templates"""
    class Meta:
        model = JobTemplate
        fields = ('name', 'job_title', 'employer', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'employer': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

