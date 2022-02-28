
from django.db import models
from django.forms import ModelForm, Textarea, IntegerField
from BookClub.models import ForumPost


class CreatePostForm(ModelForm):
    
    class Meta:
        model = ForumPost
        fields = ['title', 'content']
        
        widgets = {
            'content' : Textarea
        }