from django import forms
from django.utils.translation import gettext_lazy as _
from ..models import Category


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    class Meta:
        model = Category
        fields = ('name', 'color')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
        labels = {
            'name': _('Category Name'),
            'color': _('Color'),
        }

