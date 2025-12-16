from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Attachment


class AttachmentForm(forms.ModelForm):
    """Form for uploading attachments"""
    class Meta:
        model = Attachment
        fields = ('file', 'description')
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Optional description')}),
        }

