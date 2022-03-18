from django.db import models


class Poll(models.Model):
    title = models.CharField(max_length=120, blank=False)
    club = models.ForeignKey('Club', blank=False, null=False, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True, blank=False, null=False, editable=False)
    deadline = models.DateTimeField(auto_now=False, blank=True, null=True)
    active = models.BooleanField(default=True, blank=False, null=False)

    def get_absolute_url(self):
        pass #need to implement once detail view is done

    def __str__(self):
        return f'Poll in "{str(self.club)}" on "{self.title}"'
