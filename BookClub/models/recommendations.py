"""Recommendations model."""
from django.db import models
from django.forms import JSONField


class AbstractRecommendations(models.Model):
    """An abstract recommendations model.
    
    Attributes:
        recommendations: A JSON of the AI generated recommendations.
        modified: A boolean to track whether the recommendations have been updated.
    """
    recommendations = models.JSONField(null=False, blank=False, default=list)
    modified = models.BooleanField(null=False,blank=False, default=True)
    

class UserRecommendations(AbstractRecommendations):
    """A Book recommendation for the User.
    
    Attributes:
        user: The User the recommendation is for.
    """
    user = models.ForeignKey(
        'user', on_delete=models.CASCADE, related_name="recommendations")


class ClubRecommendations(AbstractRecommendations):
    """A Book recommendation for a Club.

    Attributes:
        club: The Club the recommendation is for.
    """
    club = models.ForeignKey('club', on_delete=models.CASCADE, related_name="recommendations")