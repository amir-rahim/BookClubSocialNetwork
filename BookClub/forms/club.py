from django.forms import ModelForm, Textarea

from BookClub.models import Club


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