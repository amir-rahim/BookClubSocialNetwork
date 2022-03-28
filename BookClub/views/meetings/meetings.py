from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import reverse, redirect
from django.utils import timezone
from django.views.generic import View, DetailView, CreateView

from BookClub.forms import MeetingForm
from BookClub.helpers import *
from BookClub.models import Meeting, Club


class JoinMeetingView(LoginRequiredMixin, View):
    """Users can join meetings"""

    redirect_location = 'meeting_list'

    def get(self, *args, **kwargs):
        return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'])

    def is_actionable(self, current_user, meeting):
        """Check if user can join a meeting"""

        return (not meeting.get_members().filter(
            username=current_user.username).exists()) and meeting.get_meeting_time() > timezone.now()

    def is_not_actionable(self):
        """If user cannot join meeting"""

        return messages.info(self.request, "You cannot join this meeting.")

    def action(self, current_user, meeting):
        """User joins the meeting"""

        messages.success(self.request, "You have joined the meeting.")
        meeting.join_member(current_user)

    def post(self, *args, **kwargs):

        try:
            meeting = Meeting.objects.get(id=kwargs['meeting_id'])
            current_user = self.request.user
        except:
            messages.error(self.request, "Error, meeting not found.")
            return redirect(self.redirect_location, club_url_name=kwargs['club_url_name'])

        if self.is_actionable(current_user, meeting):
            self.action(current_user, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, club_url_name=kwargs['club_url_name'])


class LeaveMeetingView(LoginRequiredMixin, View):
    """Users can leave meetings"""

    redirect_location = 'meeting_list'

    def get(self, *args, **kwargs):
        return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'])

    def is_actionable(self, current_user, meeting):
        """Check if user can leave a meeting"""

        return (meeting.get_members().filter(username=current_user.username).exists()) and (
                meeting.get_organiser() != current_user) and meeting.get_meeting_time() > timezone.now()

    def is_not_actionable(self):
        """If user cannot leave meeting"""

        return messages.info(self.request, "You cannot leave this meeting.")

    def action(self, current_user, meeting):
        """User leave the meeting"""

        messages.success(self.request, "You have left the meeting.")
        meeting.leave_member(current_user)

    def post(self, request, *args, **kwargs):

        try:
            meeting = Meeting.objects.get(id=kwargs['meeting_id'])
            current_user = self.request.user
        except:
            messages.error(self.request, "Error, meeting not found.")
            return redirect(self.redirect_location, club_url_name=kwargs['club_url_name'])

        if self.is_actionable(current_user, meeting):
            self.action(current_user, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, club_url_name=self.kwargs['club_url_name'])


class CreateMeetingView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Class for club owners and moderators creating meetings for the club"""

    model = Meeting
    form_class = MeetingForm
    template_name = 'meeting/create_meeting.html'

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
        except ObjectDoesNotExist:
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
        return reverse('meeting_list', kwargs={'club_url_name': self.kwargs['club_url_name']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['current_club'] = club
        return context


class DeleteMeetingView(LoginRequiredMixin, View):
    redirect_location = 'meeting_list'

    def is_actionable(self, current_user, club, meeting):
        return has_owner_rank(self.request.user, club) or (meeting.get_organiser() == current_user)

    def is_not_actionable(self):
        messages.error(self.request, f"You are not allowed to delete the meeting!")

    def action(self, current_user, club, meeting):
        meeting.delete()
        messages.success(self.request, "You have deleted the meeting.")

    def post(self, request, *args, **kwargs):
        try:
            meeting = Meeting.objects.get(id=self.kwargs['meeting_id'])
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            current_user = self.request.user
        except:
            messages.error(self.request, "Error, meeting not found.")
            return redirect(self.redirect_location, kwargs['club_url_name'])

        if self.is_actionable(current_user, club, meeting):
            self.action(current_user, club, meeting)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, kwargs['club_url_name'])

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, kwargs['club_url_name'])


class MeetingDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View to display meeting details"""
    template_name = 'meeting/meeting_details.html'
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
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['user'] = self.request.user
        return context
