"""Calendar"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from django.shortcuts import reverse, redirect
from BookClub.forms import MeetingForm
from BookClub.models import User, Club, ClubMembership, Meeting
from BookClub.helpers import *
from django.db.models import Q
import datetime


class CalendarView(LoginRequiredMixin, ListView):
    """View to display calendar agenda"""
    template_name = 'calendar.html'

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        today = datetime.date.today()
        subquery = Meeting.objects.filter(Q(members=user.id, meeting_time__gte=today)).order_by('meeting_time')

        return subquery

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        context['meetings'] = self.get_queryset()
        context['today'] = datetime.date.today()

        return context
