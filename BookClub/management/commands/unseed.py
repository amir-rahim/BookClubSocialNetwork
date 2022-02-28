from django.core.management.base import BaseCommand
from BookClub.models import User, Club, ClubMembership, Book, BookReview

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

            print('Done!')