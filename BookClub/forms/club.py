from django.forms import ModelForm, Textarea, ValidationError
from django.core.validators import RegexValidator
from django.test import tag
from BookClub.models.club import Club
from BookClub.models.user import User


class ClubForm(ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'tagline', 'rules', 'is_private']

        widgets = {
            'description': Textarea,
        }

        labels = {
            'is_private': 'Set book club as private'
        }