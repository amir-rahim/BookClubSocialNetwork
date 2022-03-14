from django.db import models

from BookClub.models.user import User


class Option(models.Model):
    text = models.CharField(max_length=120, blank=False)
    poll = models.ForeignKey('Poll', blank=False, null=False, on_delete=models.CASCADE)
    book = models.ForeignKey('Book', blank=True, null=True, on_delete=models.SET_NULL)
    voted_by = models.ManyToManyField(User, related_name='voters')
