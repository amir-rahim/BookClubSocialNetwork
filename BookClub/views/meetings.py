from django.views.generic import View, DetailView
from BookClub.helpers import *
from BookClub.models import Meeting
from BookClub.helpers import *
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
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

class MeetingDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View to display meeting details"""
    template_name = 'meeting_details.html'
    model = Meeting
    pk_url_kwarg = 'meeting_id'
    context_object_name = 'meeting'
    redirect_location='home' # should be meeting list
    
    # Redirect if club is private and user is not a member
    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name = self.kwargs['club_url_name'])
            if current_club.is_private and not current_club.is_member(self.request.user):
                messages.add_message(self.request, messages.ERROR, 'This club is private')
                return False
            else:
                return True
        except:
            return False
        
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect('available_clubs')

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        # Overrides get_context_data for context other than meetings
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(club_url_name = self.kwargs['club_url_name'])
        context['user'] = self.request.user
        return context
