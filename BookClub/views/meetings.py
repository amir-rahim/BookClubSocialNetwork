from django.views.generic import View
from BookClub.helpers import *
from BookClub.models import Meeting
from BookClub.helpers import *
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

class JoinMeetingView(LoginRequiredMixin, View):
    """Users can join meetings"""

    redirect_location = 'home' # should be list of meetings

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location)

    def is_actionable(self, currentUser, meeting):
        """Check if user can join a meeting"""

        return (not meeting.get_members().filter(username = currentUser.username).exists()) and meeting.get_meeting_time() > timezone.now()

    def is_not_actionable(self):
        """If user cannot join meeting"""

        return messages.info(self.request, "You cannot join this meeting.")

    def action(self, currentUser, meeting):
        """User joins the meeting"""

        messages.success(self.request, "You have joined the meeting.")
        meeting.join_member(currentUser)

    def post(self, request, *args, **kwargs):

        try:
            meeting = Meeting.objects.get(id=self.kwargs['meeting_id'])
            currentUser = self.request.user
        except:
            messages.error(self.request, "Error, meeting not found.")
            return redirect(self.redirect_location)

        if (self.is_actionable(currentUser, meeting)):
            self.action(currentUser, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location)

class LeaveMeetingView(LoginRequiredMixin, View):
    """Users can leave meetings"""

    redirect_location = 'home' # list of meetings

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location)

    def is_actionable(self, currentUser, meeting):
        """Check if user can leave a meeting"""

        return (meeting.get_members().filter(username = currentUser.username).exists()) and (meeting.get_organiser() != currentUser) and meeting.get_meeting_time() > timezone.now()

    def is_not_actionable(self):
        """If user cannot leave meeting"""

        return messages.info(self.request, "You cannot leave this meeting.")

    def action(self, currentUser, meeting):
        """User leave the meeting"""

        messages.success(self.request, "You have left the meeting.")
        meeting.leave_member(currentUser)

    def post(self, request, *args, **kwargs):

        try:
            meeting = Meeting.objects.get(id=self.kwargs['meeting_id'])
            currentUser = self.request.user
        except:
            messages.error(self.request, "Error, meeting not found.")
            return redirect(self.redirect_location)

        if (self.is_actionable(currentUser, meeting)):
            self.action(currentUser, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location)