from django.db import models
from BookClub.models.rated_content import *

class BookReview(TextPost):
    class Meta:
        unique_together =['book', 'creator']

    RATINGS = [(0,0), (1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)]

    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    book_rating = models.IntegerField(verbose_name='Rating', choices=RATINGS, default=0, blank=False, null=False)


class BookReviewComment(TextComment):

    book_review = models.ForeignKey('BookReview', blank = False, null = False, on_delete=models.CASCADE)
