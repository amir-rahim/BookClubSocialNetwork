"""Featured Books model."""
from django.db import models

from BookClub.models import Club, Book

class FeaturedBooks(models.Model):
    """Class for featuring a Book in a Club.
    
    Attributes:
        club: The Club the Book is being featured in.
        book: The Book that is being featured.
        reason: A string the contains the reason the User featured the Book.
    """
    club = models.ForeignKey(Club, blank=False, null=False, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, blank=False, null=False, on_delete=models.CASCADE)
    reason = models.CharField(blank=True, max_length=50)

    @staticmethod
    def get_books(club):
        return FeaturedBooks.objects.filter(club=club)
        