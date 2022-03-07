"""Calendar"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.shortcuts import reverse, redirect
from BookClub.forms import MeetingForm
from BookClub.models import User, Club, ClubMembership, Meeting
from BookClub.helpers import *


class CalendarView(LoginRequiredMixin, ListView):
    """View to display calendar agenda"""
    template_name = 'calendar.html'

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        inner_qs = User.objects.filter(username__contains=Meeting.members.username)
        subquery = Meeting.objects.filter(members__id=inner_qs)
        return subquery

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        # user = User.objects.get(id=self.request.user.id)
        # try:
        #     # if beer.salas_set.filter(pk=sala.pk).exists():
        #     # inner_qs = Blog.objects.filter(name__contains='Cheddar')
        #     # entries = Entry.objects.filter(blog__in=inner_qs)
        #     inner_qs = User.objects.filter(id__in=user.id)
        #     meetings = Meeting.objects.filter(user__in=inner_qs)
        # except:
        #     meetings = None
        context['meetings'] = self.get_queryset()

        return context
