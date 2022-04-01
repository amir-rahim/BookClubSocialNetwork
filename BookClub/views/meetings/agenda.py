"""Agenda related views."""
import datetime
import pytz

import vobject as vobject
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView
from icalendar import Calendar
from BookClub.helpers import *
from BookClub.models import Meeting


class AgendaView(LoginRequiredMixin, ListView):
    """Render all meetings in the user's agenda."""
    template_name = 'meeting/agenda.html'

    def get_queryset(self):
        user = User.objects.get(id=self.request.user.id)
        today = pytz.utc.localize(datetime.datetime.today())
        subquery = Meeting.objects.filter(Q(members=user.id, meeting_time__gte=today)).order_by('meeting_time')

        return subquery

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        club_ids = get_memberships_with_access(self.request.user)
        clubs = Club.objects.filter(id__in=club_ids)

        context = super().get_context_data(**kwargs)
        context['meetings'] = self.get_queryset()
        today = datetime.date.today()
        context['joined_today'] = Meeting.objects.filter(club__in=clubs, members=self.request.user.id, meeting_time__date=today).order_by('meeting_time')
        context['joined_upcoming'] = Meeting.objects.filter(club__in=clubs, members=self.request.user.id, meeting_time__date__gt=today).order_by('meeting_time')
        context['not_joined_today'] = Meeting.objects.filter(club__in=clubs, meeting_time__date=today).exclude(members=self.request.user.id).order_by('meeting_time')
        context['not_joined_upcoming'] = Meeting.objects.filter(club__in=clubs, meeting_time__date__gt=today).exclude(members=self.request.user.id).order_by('meeting_time')
        context['all_meetings_today'] = Meeting.objects.filter(club__in=clubs, meeting_time__date=today).order_by('meeting_time')
        context['all_meetings_upcoming'] = Meeting.objects.filter(club__in=clubs, meeting_time__date__gt=today).order_by('meeting_time')
        context['current_user'] = self.request.user

        return context


class ExportCalendarView(View):
    """Allow the user to export their agenda."""

    def get(self, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        today = pytz.utc.localize(datetime.datetime.today())
        meetings = Meeting.objects.filter(Q(members=user.id, meeting_time__gte=today)).order_by('meeting_time')

        cal = vobject.iCalendar()
        cal.add('method').value = 'PUBLISH'  # IE/Outlook needs this

        for meeting in meetings:
            vevent = cal.add('vevent')
            vevent.add('dtstart').value = meeting.meeting_time
            vevent.add('dtend').value = meeting.meeting_end_time
            vevent.add('dtstamp').value = datetime.datetime.now(tz=pytz.UTC)
            vevent.add('summary').value = meeting.title
            vevent.add('uid').value = str(meeting.id)
            vevent.add('location').value = meeting.location
            vevent.add('description').value = meeting.description
        icalstream = cal.serialize()
        response = HttpResponse(icalstream, content_type='text/calendar')
        response['Filename'] = 'agenda.ics'  # IE needs this
        response['Content-Disposition'] = 'attachment; filename=agenda.ics'
        return response
