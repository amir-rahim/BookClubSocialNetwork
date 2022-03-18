from django.db import models
from BookClub.models import RatedContent
from django.utils.text import slugify


class TextComment(RatedContent):
    class Meta:
        abstract = True

    content = models.CharField(max_length=240, blank=False)


class TextPost(RatedContent):
    class Meta:
        abstract = True

    title = models.CharField(max_length=30, blank=False)
    content = models.CharField(max_length=1024, blank=False)
    slug = models.SlugField(max_length=30)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
