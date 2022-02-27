from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from BookClub.models import UserCreatedObject

class RatedContent(UserCreatedObject):

    class Meta:
        abstract = True
        ordering = ['rating']

    rating = models.IntegerField(
        blank=False, null=False, default=0, auto_created=True)
    votes = models.ManyToManyField('Vote', blank=True)

    def update_rating(self):
        count = 0
        for vote in self.votes:
            if vote.type:
                count += 1
            else:
                count -= 1

        self.rating = count
        return self.get_rating()

    def get_rating(self):
        return self.rating

    def add_vote(self, vote):
        if vote.type:
            self.rating = self.rating + 1
        else:
            self.rating = self.rating - 1
        self.votes.add(vote)
        self.save(update_fields=['rating'])

    def remove_vote(self, vote):
        if vote.type:
            self.rating = self.rating - 1
        else:
            self.rating = self.rating + 1
        self.votes.remove(vote)
        self.save(update_fields=['rating'])


class Vote(UserCreatedObject):

    class Meta:
        unique_together = [['creator', 'object_id', 'content_type']]

    type = models.BooleanField(
        verbose_name='Vote type', null=True, blank=False)
    content_type = models.ForeignKey(
        ContentType, blank=False, null=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        if self.target:
            super().save()
            self.target.add_vote(self)
        else:
            raise Exception()

    def delete(self, *args, **kwargs):
        if self.target:
            self.target.remove_vote(self)
        super().delete()
