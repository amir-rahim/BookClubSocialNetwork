from django.db import models

from BookClub.models import Club, Book

class FeaturedBooks(models.Model):
    """ Class for featuring a book"""

    club = models.ForeignKey(Club, blank=False, null=False, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, blank=False, null=False, on_delete=models.CASCADE)
    reason = models.CharField(blank=True, max_length=50)

    @staticmethod
    def get_books(club):
        return FeaturedBooks.objects.filter(club=club)
        