from django.core.management.base import BaseCommand
from BookClub.models import *

class Command(BaseCommand):
        """The database unseeder."""
        def __init__(self):
            super().__init__()
        def add_arguments(self, parser):

            parser.add_argument('--complete', '--c', action="store_true")
        def handle(self, *args, **options):
            print('Unseeding...')
            if options['complete']:
                User.objects.filter(is_superuser=False).delete()
                Book.objects.all().delete()
                BookReview.objects.all().delete()
            Club.objects.all().delete()
            ClubMembership.objects.all().delete()
            ForumPost.objects.all().delete()
            ForumComment.objects.all().delete()
            Forum.objects.all().delete()
            Vote.objects.all().delete()
            Meeting.objects.all().delete()
            UserRecommendations.objects.all().delete()
            ClubRecommendations.objects.all().delete()
            BookList.objects.all().delete()
            FeaturedBooks.objects.all().delete()
            BookReviewComment.objects.all().delete()
            UserToUserRelationship.objects.all().delete()
            Vote.objects.all().delete()         
            
            print('Done!')