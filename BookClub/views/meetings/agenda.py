"""Agenda Related Views"""
import datetime, pytz

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from BookClub.helpers import *
from BookClub.models import Meeting


class AgendaView(LoginRequiredMixin, ListView):
    """View to display agenda"""
    template_name = 'agenda.html'

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        today = pytz.utc.localize(datetime.datetime.today())
        subquery = Meeting.objects.filter(Q(members=user.id, meeting_time__gte=today)).order_by('meeting_time')

        return subquery

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        club_ids = ClubMembership.objects.filter(user=self.request.user).values_list('club', flat=True)
        clubs = Club.objects.filter(id__in=club_ids)
        not_joined = Meeting.objects.filter(club__in=clubs).exclude(members=self.request.user.id)
        all_meetings = Meeting.objects.filter(club__in=clubs)
        context = super().get_context_data(**kwargs)
        context['meetings'] = self.get_queryset()
        context['today'] = datetime.date.today()
        context['not_joined'] = not_joined
        context['all_meetings'] = all_meetings
        context['current_user'] = self.request.user

        return context
