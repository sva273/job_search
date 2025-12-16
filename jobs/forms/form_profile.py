from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'theme', 'email_notifications_enabled', 'reminder_days_before']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'email_notifications_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reminder_days_before': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 30}),
        }
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'theme': _('Theme'),
            'email_notifications_enabled': _('Email Notifications Enabled'),
            'reminder_days_before': _('Reminder Days Before'),
        }

