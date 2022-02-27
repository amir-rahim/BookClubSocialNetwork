from django.db import models
from BookClub.models import RatedContent

class TextComment(RatedContent):
    class Meta:
        abstract = True

    content = models.CharField(max_length=240, blank=False)


class TextPost(RatedContent):

    class Meta:
        abstract = True

    title = models.CharField(max_length=30, blank=False)
    content = models.CharField(max_length=1024, blank=False)
