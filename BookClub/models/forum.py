from django.db import models
from django.utils.text import slugify
from django.urls import reverse

from BookClub.models import TextPost, TextComment


class Forum(models.Model):
    class Meta:
        unique_together = [['title', 'associated_with']]

    title = models.CharField(max_length=30, blank=False, null=False)
    associated_with = models.OneToOneField(
        'Club', on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(max_length=30, blank=False, null=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_posts(self):
        return self.forumpost_set.all()

    def get_absolute_url(self):
        if self.associated_with is None:
            return reverse('global_forum')
        return reverse('club_forum', kwargs={'club_url_name': self.associated_with.club_url_name})

    def __str__(self):
        if self.associated_with is None:
            return f'Global Forum'
        return f'{self.title}'


class ForumPost(TextPost):
    class Meta:
        ordering = ['-created_on']

    forum = models.ForeignKey('Forum', blank=False, null=False, on_delete=models.CASCADE)

    def get_comments(self):
        return self.forumcomment_set.all()

    def get_absolute_url(self):
        return self.forum.get_absolute_url() + f'{self.pk}/'

    def __str__(self):
        return f'"{self.title}" post on {str(self.forum)} by {str(self.creator)}'


class ForumComment(TextComment):
    class Meta:
        ordering = ['-created_on']

    post = models.ForeignKey('ForumPost', on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment by {str(self.creator)} on {str(self.post)}'
