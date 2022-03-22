from django.db import models
from django.forms import JSONField


class AbstractRecommendations(models.Model):
    recommendations = models.JSONField(null=False, blank=False, default=list)
    modified = models.BooleanField(null=False,blank=False, default=True)
    

class UserRecommendations(AbstractRecommendations):
    user = models.ForeignKey(
        'user', on_delete=models.CASCADE, related_name="recommendations")


class ClubRecommendations(AbstractRecommendations):
    club = models.ForeignKey('club', on_delete=models.CASCADE, related_name="recommendations")