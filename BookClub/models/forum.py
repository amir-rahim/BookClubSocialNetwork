from django.db import models
from BookClub.models import TextPost, RatedContent
from BookClub.models.rated_content import TextComment

class ForumPost(TextPost):
    class Meta:
        ordering = ['-created_on']
        
    comments = models.ManyToManyField('ForumComment', related_name='Comments', blank=True)
    
class ForumComment(TextComment):
    
    subComments = models.ManyToManyField('ForumComment', related_name='Replies', blank=True)

class Forum(models.Model):
    class Meta:
        unique_together = [['title','associatedWith']]
        
    title = models.CharField(max_length=30, blank=False, null=False)
    posts = models.ManyToManyField('ForumPost', related_name='Posts', blank=True)
    associatedWith = models.ForeignKey('Club', on_delete=models.CASCADE, blank=True)
