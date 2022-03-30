"""Vote related form."""
from django import forms

from BookClub.models import Vote


class VoteForm(forms.ModelForm):
    """Form to allow users to vote on posts."""
    class Meta:
        model = Vote
        fields = ['creator', 'type', 'content_type', 'object_id']
