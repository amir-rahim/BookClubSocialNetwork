from django.db import models
from django.core.exceptions import ValidationError

from BookClub.models.user import User

class Club(models.Model):
    name = models.CharField(unique = False, max_length = 100, blank = False)
    description = models.CharField(max_length = 200, blank = False)
    rules = models.CharField(max_length = 200, blank = True)
    is_private = models.BooleanField(default = False, blank = False, null = False)
    created_on = models.DateField(auto_now_add = True)


    def __str__(self):
        return self.name
