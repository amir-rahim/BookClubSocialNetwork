"""Model for user created objects."""
from django.db import models


class UserCreatedObject(models.Model):
    """Abstract class for giving all our UserCreatedObjects a creator(User) and a created_on field.
    
    Attributes:
        creator: A User that is the creator of the object.
        created_on: A DateTime field that the object was created on.
    """

    class Meta:
        abstract = True
        ordering = ['-created_on']

    creator = models.ForeignKey(
        'BookClub.User', blank=False, null=False, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
