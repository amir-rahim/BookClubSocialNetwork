from django.db import models


class BookReview(models.Model):
    class Meta:
        unique_together = ['book', 'user']

    RATINGS = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]

    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    rating = models.IntegerField(verbose_name='Ratings', choices=RATINGS, default=0, blank=False, null=False)
    review = models.CharField(verbose_name="Review:", max_length=1024, blank=True, null=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    createdOn = models.DateTimeField(verbose_name="Reviewed on:", auto_now=True, blank=False, null=False)
