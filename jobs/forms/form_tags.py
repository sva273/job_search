from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Tag


class TagForm(forms.ModelForm):
    """Form for creating/editing tags"""
    class Meta:
        model = Tag
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Tag Name'),
        }

