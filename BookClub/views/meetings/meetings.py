from django.views.generic import View, DetailView, CreateView
from BookClub.helpers import *
from BookClub.models import Meeting, Club
from BookClub.forms import MeetingForm
from BookClub.helpers import *
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone


class JoinMeetingView(LoginRequiredMixin, View):
    """Users can join meetings"""

    redirect_location = 'meeting_details'

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'],
                        meeting_id=self.kwargs['meeting_id'])

    def is_actionable(self, currentUser, meeting):
        """Check if user can join a meeting"""

        return (not meeting.get_members().filter(
            username=currentUser.username).exists()) and meeting.get_meeting_time() > timezone.now()

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
            return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'],
                            meeting_id=self.kwargs['meeting_id'])

        if (self.is_actionable(currentUser, meeting)):
            self.action(currentUser, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'],
                        meeting_id=self.kwargs['meeting_id'])


class LeaveMeetingView(LoginRequiredMixin, View):
    """Users can leave meetings"""

    redirect_location = 'meeting_details'

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'],
                        meeting_id=self.kwargs['meeting_id'])

    def is_actionable(self, currentUser, meeting):
        """Check if user can leave a meeting"""

        return (meeting.get_members().filter(username=currentUser.username).exists()) and (
                    meeting.get_organiser() != currentUser) and meeting.get_meeting_time() > timezone.now()

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
            return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'],
                            meeting_id=self.kwargs['meeting_id'])

        if (self.is_actionable(currentUser, meeting)):
            self.action(currentUser, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'],
                        meeting_id=self.kwargs['meeting_id'])


class CreateMeetingView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Class for club owners and moderators creating meetings for the club"""

    model = Meeting
    form_class = MeetingForm
    template_name = 'create_meeting.html'

    # Redirect if user is not a moderator or owner of the club
    def test_func(self):
        try:
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            if not (has_owner_rank(self.request.user, club) or has_moderator_rank(self.request.user, club)):
                if club.is_private == False or has_member_rank(self.request.user, club):
                    messages.error(self.request, 'Only the owner and moderators can create meetings!')
                    return False
                else:
                    return False
            else:
                return True
        except:
            messages.error(self.request, 'Club not found or you are not a member of this club')
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect('club_dashboard', self.kwargs['club_url_name'])

    def form_valid(self, form):
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        meeting = form.save(commit=False)
        meeting.organiser = self.request.user
        meeting.club = club
        meeting.save()
        meeting.join_member(self.request.user)
        messages.success(self.request, 'Successfully created a new meeting!')
        return super(CreateMeetingView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "The data provided was invalid!")
        return super().form_invalid(form);

    def get_success_url(self):
        # Change to redirect to list of meetings
        return reverse('create_meeting', kwargs={'club_url_name': self.kwargs['club_url_name']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['current_club'] = club
        return context


class DeleteMeetingView(LoginRequiredMixin, View):
    redirect_location = 'meeting_list'

    def is_actionable(self, currentUser, club, meeting):
        return has_owner_rank(self.request.user, club) or (meeting.get_organiser() == currentUser)

    def is_not_actionable(self):
        messages.error(self.request, f"You are not allowed to delete the meeting!")

    def action(self, currentUser, club, meeting):
        delete_meeting(meeting)
        messages.success(self.request, "You have deleted the meeting.")

    def post(self, request, *args, **kwargs):

        try:
            meeting = Meeting.objects.get(id=self.kwargs['meeting_id'])
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            currentUser = self.request.user
        except:
            messages.error(self.request, "Error, meeting not found.")
            return redirect(self.redirect_location, kwargs['club_url_name'])

        if self.is_actionable(currentUser, club, meeting):
            self.action(currentUser, club, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, kwargs['club_url_name'])

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, kwargs['club_url_name'])


class MeetingDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View to display meeting details"""
    template_name = 'meeting_details.html'
    model = Meeting
    pk_url_kwarg = 'meeting_id'
    context_object_name = 'meeting'
    redirect_location = 'home'  # should be meeting list

    # Redirect if club is private and user is not a member
    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
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
        context['club'] = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['user'] = self.request.user
        return context
