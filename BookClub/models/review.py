from django.db import models
from django.urls import reverse
from BookClub.models.rated_content import *

class BookReview(TextPost):
    class Meta:
        unique_together =['book', 'creator']

    RATINGS = [(0,0), (1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (9,9), (10,10)]

    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    book_rating = models.IntegerField(verbose_name='Rating', choices=RATINGS, default=0, blank=False, null=False)

    def get_comments(self):
        return self.bookreviewcomment_set.all()

    def get_delete_url(self):
        return reverse('delete_review', kwargs={'book_id': self.book.pk})

    def __str__(self):
        return f'{self.book_rating}/10 rating & review by {str(self.creator)} on "{str(self.book)}"'

class BookReviewComment(TextComment):

    book_review = models.ForeignKey('BookReview', blank = False, null = False, on_delete=models.CASCADE)

    def get_delete_url(self):
        kwargs={
            'book_id': self.book_review.book.pk,
            'review_id': self.book_review.pk,
            'comment_id': self.pk
        }
        return reverse('delete_review_comment', kwargs=kwargs)

    def __str__(self):
        return f'Comment by {str(self.creator)} on {str(self.book_review)}'
