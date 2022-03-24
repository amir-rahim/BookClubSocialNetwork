from django.core.management.base import BaseCommand
from BookClub.models import Book
from django.db.models import Count
class Command(BaseCommand):
    """The database seeder."""

    def handle(self, *args, **options):
        books = Book.objects.all().values('ISBN',count=Count('bookreview'))
        newlist = sorted(books, key=lambda d: d['count'], reverse=True)
        sl = newlist[:10000]
        print(sl);