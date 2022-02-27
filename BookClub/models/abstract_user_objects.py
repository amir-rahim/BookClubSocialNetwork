from django.db import models

class UserCreatedObject(models.Model):

    class Meta:
        abstract = True
    
    creator = models.ForeignKey(
        'BookClub.User', blank=False, null=False, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    
    
