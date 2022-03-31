"""Forum related forms."""
from django.forms import ModelForm, Textarea

from BookClub.models import ForumPost, ForumComment


class CreatePostForm(ModelForm):
    """To create a new form post."""
    class Meta:
        model = ForumPost
        fields = ['title', 'content']

        widgets = {
            'content': Textarea
        }


class CreateForumCommentForm(ModelForm):
    """To create a forum comment."""
    class Meta:
        model = ForumComment
        fields = ['content']

        widgets = {
            'content': Textarea
        }
