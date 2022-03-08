from django.db import models

class UserCreatedObject(models.Model):
    """ Abstract class for giving all our UserCreatedObjects a creator(User) and a created_on field """
    class Meta:
        abstract = True
    
    creator = models.ForeignKey(
        'BookClub.User', blank=False, null=False, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    
    
