from django import forms

from BookClub.models import Vote


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['creator', 'type', 'content_type', 'object_id']
