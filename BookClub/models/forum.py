from django.db import models
from django.utils.text import slugify

from BookClub.models import TextPost, TextComment


class ForumPost(TextPost):
    class Meta:
        ordering = ['-created_on']

    def get_comments(self):
        return self.forumcomment_set.all()


class ForumComment(TextComment):
    class Meta:
        ordering = ['-created_on']

    post = models.ForeignKey('ForumPost', on_delete=models.CASCADE)


class Forum(models.Model):
    class Meta:
        unique_together = [['title', 'associated_with']]

    title = models.CharField(max_length=30, blank=False, null=False)
    posts = models.ManyToManyField('ForumPost', related_name='Posts', blank=True)
    associated_with = models.OneToOneField(
        'Club', on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(max_length=30)

    def add_post(self, post):
        self.posts.add(post)
        self.save()

    def remove_post(self, post):
        self.posts.remove(post)
        self.save()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
