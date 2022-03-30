"""Review model."""
from django.db import models
from django.urls import reverse
from BookClub.models.rated_content import *
from BookClub.models.recommendations import UserRecommendations


class BookReview(TextPost):
    """Allow the User to Review a Book.
    
    Attributes:
        book: The Book that is being reviewed.
        book_rating: The rating the User has given the Book.
    """
    class Meta:
        ordering = ['-created_on']
        unique_together = ['book', 'creator']

    RATINGS = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]

    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    book_rating = models.IntegerField(verbose_name='Rating', choices=RATINGS, default=0, blank=False, null=False)

    def get_comments(self):
        return self.bookreviewcomment_set.all()

    def get_delete_url(self):
        return reverse('delete_review', kwargs={'book_id': self.book.pk})

    def __str__(self):
        return f'{self.book_rating}/10 rating & review by {str(self.creator)} on "{str(self.book)}"'

    def str(self):
        return self.__str__()

    def get_delete_str(self):
        return self.__str__()

    def save(self, **kwargs):
        super().save(**kwargs)
        if UserRecommendations.objects.filter(user=self.creator).exists():
            UserRecommendations.objects.get(user=self.creator).modified = True


class BookReviewComment(TextComment):
    """Allow the User to Comment under a Review.
    
    Attributes:
        book_review: The Review the Comment is under.
    """
    book_review = models.ForeignKey('BookReview', blank=False, null=False, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_on']

    def get_delete_url(self):
        kwargs = {
            'book_id': self.book_review.book.pk,
            'review_id': self.book_review.pk,
            'comment_id': self.pk
        }
        return reverse('delete_review_comment', kwargs=kwargs)

    def __str__(self):
        return f'Comment by {str(self.creator)} on {str(self.book_review)}'

    def str(self):
        return self.__str__()

    def get_delete_str(self):
        return self.__str__()
