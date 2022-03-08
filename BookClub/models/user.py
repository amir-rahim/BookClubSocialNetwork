from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from BookClub.recommender_module.recommenders.popular_books_recommender import PopularBooksRecommender
from BookClub.models.review import BookReview


class User(AbstractUser):
    """User model used for authentication."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[A-Za-z0-9]([._-](?![._-])|[A-Za-z0-9])*[A-Za-z0-9]$',
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

    """Get the 10 most popular books recommended to the user (that the user has not read yet).
        Returns a list of ISBN numbers."""
    def get_popularity_recommendations(self):
        user_read_books = self.get_read_books()
        # Import Popular Books recommender
        popular_books = PopularBooksRecommender()
        recommended_books = popular_books.get_recommendations_from_average_and_median(user_read_books=user_read_books)
        return recommended_books

    """Get a list of all books that the user has read."""
    def get_read_books(self):
        try:
            user_reviews = BookReview.objects.get(user=self)
        except:
            user_reviews = []
        isbn_list = []
        for review in user_reviews:
            isbn_list.append(review.book.ISBN)
        return isbn_list

    """Get (up to) 10 book recommendations, from books the user has rated."""
    def get_item_based_recommendations(self, positive_ratings_only=True):
        user_read_books = self.get_read_books()
