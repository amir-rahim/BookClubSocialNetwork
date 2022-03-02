from django.db import models
from BookClub.models import TextPost, RatedContent, TextComment


class ForumPost(TextPost):
    class Meta:
        ordering = ['-created_on']

    comments = models.ManyToManyField('ForumComment', related_name='Comments', blank=True)

    def add_comment(self, comment):
        self.comments.add(comment)
        self.save()

    def remove_comment(self, comment):
        self.comments.remove(comment)
        self.save()


class ForumComment(TextComment):
    subComments = models.ManyToManyField('ForumComment', related_name='Replies', blank=True)

    def add_comment(self, comment):
        self.subComments.add(comment)
        self.save()

    def remove_comment(self, comment):
        self.subComments.remove(comment)
        self.save()


class Forum(models.Model):
    class Meta:
        unique_together = [['title', 'associatedWith']]

    title = models.CharField(max_length=30, blank=False, null=False)
    posts = models.ManyToManyField('ForumPost', related_name='Posts', blank=True)
    associatedWith = models.OneToOneField(
        'Club', on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(max_length=30)

    def add_post(self, post):
        self.posts.add(post)
        self.save()

    def remove_post(self, post):
        self.posts.remove(post)
        self.save()
