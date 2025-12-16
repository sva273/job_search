from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=150, required=False, label=_('First Name'))
    last_name = forms.CharField(max_length=150, required=False, label=_('Last Name'))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _('Username')
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Password confirmation')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            # Create or update UserProfile
            from ..models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.first_name = self.cleaned_data.get('first_name', '')
            profile.last_name = self.cleaned_data.get('last_name', '')
            profile.save()
        return user

