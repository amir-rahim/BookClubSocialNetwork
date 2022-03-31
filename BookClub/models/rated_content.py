"""Rated content model."""
from django.db import models
from BookClub.models import RatedContent
from django.utils.text import slugify


class TextComment(RatedContent):
    """An abstract model allowing Users to make Comments.
    
    Attributes:
        content: A string containing the content of the Comment.
    """
    class Meta:
        abstract = True

    content = models.CharField(max_length=240, blank=False)


class TextPost(RatedContent):
    """An abstract model allowing Users to make Posts.
    
    Attributes:
        title: A string containing the title of the Post.
        content: A string containing the contents of the Post.
        slug: A Slug for the URL.
    """
    class Meta:
        abstract = True

    title = models.CharField(max_length=30, blank=False)
    content = models.CharField(max_length=1024, blank=False)
    slug = models.SlugField(max_length=30)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
