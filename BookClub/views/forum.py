"""Forum Related Views"""
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView

from BookClub.models import ForumPost, Forum


def global_forum_view(request):
    """This is the library dashboard view."""
    return render(request, 'global_forum.html')
