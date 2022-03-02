from django.forms import ModelForm, Textarea

from BookClub.models import ForumPost, ForumComment


class CreatePostForm(ModelForm):
    class Meta:
        model = ForumPost
        fields = ['title', 'content']

        widgets = {
            'content': Textarea
        }


class CreateForumCommentForm(ModelForm):
    class Meta:
        model = ForumComment
        fields = ['content']

        widgets = {
            'content': Textarea
        }
