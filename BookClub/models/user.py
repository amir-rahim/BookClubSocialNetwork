from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from libgravatar import Gravatar


class User(AbstractUser):
    """User model used for authentication."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[^._][-a-zA-Z0-9._]*[^._]$',
                message='Usernames may only contain lowercase characters '
                        'and . _ - but not as '
                        'the first or last character.',
                code='invalid_username'
            )
        ]
    )

    email = models.EmailField(unique=True, blank=False)
    public_bio = models.CharField(max_length=250, blank=False)

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def __str__(self):
        return f'{self.username}'

    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'username': self.username})
