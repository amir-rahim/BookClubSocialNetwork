"""User model."""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from libgravatar import Gravatar


class User(AbstractUser):
    """User model used for authentication.
    
    Attributes:
        email: The Email the User creates their account with.
        public_bio: A string containing the User's public bio.
        saved_booklists: A list of the Book Lists saved by this User, made by other Users.
    """

    class Meta:
        ordering = ['username']
        
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
    saved_booklists = models.ManyToManyField("BookList", blank=True)

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def __str__(self):
        return f'{self.username}'

    def get_absolute_url(self):
        return reverse('user_profile', kwargs={'username': self.username})

    def save_booklist(self, booklist):
        self.saved_booklists.add(booklist)

    def get_saved_booklists(self):
        return self.saved_booklists.all()

    def remove_from_saved_booklists(self, booklist):
        self.saved_booklists.remove(booklist)
