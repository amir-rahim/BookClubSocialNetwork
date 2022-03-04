from django.core.management.base import BaseCommand
from BookClub.models import User, Club, ClubMembership, Book, Vote, Forum, ForumComment, ForumPost
from BookClub.models.review import *
class Command(BaseCommand):
        """The database unseeder."""
        def __init__(self):
            super().__init__()

        def handle(self, *args, **options):
            print('Unseeding...')

            User.objects.filter(is_superuser=False).delete()
            Club.objects.all().delete()
            ClubMembership.objects.all().delete()
            Book.objects.all().delete()
            BookReview.objects.all().delete()
            ForumPost.objects.all().delete()
            ForumComment.objects.all().delete()
            Forum.objects.all().delete()
            Vote.objects.all().delete()

            print('Done!')