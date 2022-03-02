from django.db import models

class Poll(models.Model):

    title = models.CharField(max_length = 120, blank = False)
    created_on = models.DateTimeField(auto_now = True, blank = False, null = False, editable = False)
    deadline = models.DateTimeField(auto_now = False, blank = True, null = True)
    active = models.BooleanField(default=True, blank=False, null=False)
