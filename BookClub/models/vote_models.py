"""Vote related models."""
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from BookClub.models import UserCreatedObject


class RatedContent(UserCreatedObject):
    """An abstract class for any of our user created objects that User's can vote on.
        All rated content will be ordered by descending rating.

    Attributes:
        rating: A integer storing the rating the User chooses.
        votes: A list of all upvotes and downvotes the object has.
    """

    class Meta:
        abstract = True
        ordering = ['rating']

    rating = models.IntegerField(
        blank=False, null=False, default=0, auto_created=True)
    votes = models.ManyToManyField('Vote', blank=True)

    def update_rating(self):
        """Force our rating to be updated, by counting the positive and negative votes and resetting our rating."""
        count = 0
        for vote in self.votes.all():
            if vote.type:
                count += 1
            else:
                count -= 1

        self.rating = count
        self.save(update_fields=['rating'])
        return self.get_rating()

    def get_rating(self):
        """Return the current rating of the content."""
        return self.rating

    def add_vote(self, vote):
        """Add the vote provided to our many-to-many-relationship of votes,
            and update our rating based on the type of vote this is."""
        if vote.type:
            self.rating = self.rating + 1
        else:
            self.rating = self.rating - 1
        self.votes.add(vote)
        self.save(update_fields=['rating'])

    def remove_vote(self, vote):
        """Remove the vote provided from our many-to-many-relationship
            and update our rating based on the type of vote this is."""
        if vote.type:
            self.rating = self.rating - 1
        else:
            self.rating = self.rating + 1
        self.votes.remove(vote)
        self.save(update_fields=['rating'])

    def get_content_type(self):
        return self.__class__


class Vote(UserCreatedObject):
    """A positive or negative Vote associated to Forum Posts, Comments and Reviews.

    Object represents a single vote, positive or negative, for an object that
    inherits from RatedContent. Votes are constrained so that a User can
    only vote once per object. A type of "true" means an upvote,
    a type of "false" means a downvote. 
    
    Attributes:
        type: A boolean of whether the vote is an upvote or a downvote.
        content_type: The Content type (the model) of the object that can be Voted on.
        object_id: The primary key of the object.
        target: The object the Vote is associated with.
    """

    class Meta:
        unique_together = [['creator', 'object_id', 'content_type']]

    type = models.BooleanField(
        verbose_name='Vote type', null=False, blank=False)
    content_type = models.ForeignKey(
        ContentType, blank=False, null=False, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    def save(self, *args, **kwargs):
        """Saves our vote, and adds the vote to the targeted objects list of votes."""
        if self.target:
            super().save()
            self.target.add_vote(self)
        else:
            raise ValueError()

    def delete(self, *args, **kwargs):
        """Deletes our vote, and removes it from the targeted objects' list of votes."""
        if self.target:
            self.target.remove_vote(self)
        super().delete()
