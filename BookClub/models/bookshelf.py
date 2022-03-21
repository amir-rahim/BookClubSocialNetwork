from django.db import models

from BookClub.models import User, Book


class BookShelf(models.Model):
    class Meta:
        ordering = ['-id']

    class ListType(models.IntegerChoices):
        TO_READ = 0
        READING = 1
        ON_HOLD = 2
        COMPLETED = 3

    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, blank=False, null=False, on_delete=models.CASCADE)
    status = models.IntegerField(choices=ListType.choices, blank=False, null=False)

    @staticmethod
    def get_to_read(user):
        return BookShelf.objects.filter(user=user, status=0)
    
    @staticmethod
    def get_reading(user):
        return BookShelf.objects.filter(user=user, status=1)
    
    @staticmethod
    def get_on_hold(user):
        return BookShelf.objects.filter(user=user, status=2)
    
    @staticmethod
    def get_completed(user):
        return BookShelf.objects.filter(user=user, status=3) 

    @staticmethod
    def get_all_books(user):
        return BookShelf.objects.filter(user=user)
