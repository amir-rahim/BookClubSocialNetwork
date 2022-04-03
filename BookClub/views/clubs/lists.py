"""Views related to club lists."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from BookClub.authentication_mixins import PrivateClubMixin

from BookClub.helpers import *
from BookClub.models import User, Club, ClubMembership, Meeting


class MembersListView(LoginRequiredMixin, PrivateClubMixin, TemplateView):
    """Render the list of members for a given club."""
    template_name = 'clubs/club_members.html'

    def handle_no_permission(self):
        url = reverse('club_dashboard', kwargs=self.kwargs)
        return redirect(url)

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        club = get_club_from_url_name(self.kwargs.get('club_url_name'))
        user = User.objects.get(id=self.request.user.id)
        try:
            rank = ClubMembership.objects.get(user=user, club=club)
        except ObjectDoesNotExist:
            rank = None
        context['club'] = club
        context['members'] = club.get_members()
        context['moderators'] = club.get_moderators()
        context['owner'] = club.get_club_owner()
        context['request_user'] = rank

        return context


class ApplicantListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Render a table of applicants for a private club."""
    template_name = 'clubs/applicant_list.html'

    def test_func(self):
        """Allow only the owner and moderators of a club to view the table of applicants."""
        try:
            user = self.request.user
            current_club = get_club_from_url_name(
                self.kwargs.get('club_url_name'))
            if not has_moderator_rank(user, current_club) and (not has_owner_rank(user, current_club)):
                messages.add_message(
                    self.request, messages.ERROR, 'Only Owners and Moderators can view this.')
                return False
            else:
                return True
        except ObjectDoesNotExist:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('club_dashboard', kwargs=self.kwargs)
            return redirect(url)

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
        context = super().get_context_data(**kwargs)
        club = get_club_from_url_name(self.kwargs.get('club_url_name'))
        user = User.objects.get(id=self.request.user.id)
        rank = ClubMembership.objects.get(user=user, club=club)
        context['club'] = club
        context['applicants'] = club.get_applicants()
        context['moderators'] = club.get_moderators()
        context['owner'] = club.get_club_owner()
        context['request_user'] = rank

        return context


class MeetingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Render a table of meetings for a given club."""
    template_name = 'meeting/club_meetings.html'
    context_object_name = 'meetings'
    paginate_by = 10

    def test_func(self):
        """Don't allow applicants of private clubs to view the list of meetings."""
        try:
            current_club = get_club_from_url_name(
                self.kwargs.get('club_url_name'))
            current_user = self.request.user
            if has_applicant_rank(current_user, current_club):
                messages.add_message(self.request, messages.ERROR,
                                     'You must be a member of this club to view meetings.')
                return False
            else:
                return True
        except ObjectDoesNotExist:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('club_dashboard', kwargs=self.kwargs)
            return redirect(url)

    def get_queryset(self):
        club = Club.objects.get(club_url_name=self.kwargs.get('club_url_name'))
        subquery = Meeting.objects.filter(club=club)
        return subquery

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(
            club_url_name=self.kwargs.get('club_url_name'))
        context['current_user'] = self.request.user

        return context


class MeetingParticipantsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Render a list of participants for a given meeting."""
    template_name = 'meeting/meeting_participants.html'
    context_object_name = 'participants'

    # Redirect if club is private and user is not a member

    def test_func(self):
        """Don't allow applicants of private clubs to view the table of meeting participants."""
        try:
            current_club = get_club_from_url_name(
                self.kwargs.get('club_url_name'))
            current_user = self.request.user
            if not has_membership_with_access(current_club, current_user):
                messages.add_message(self.request, messages.ERROR,
                                     'You must be a member of this club to view this meeting\'s participants.')
                return False
            else:
                return True
        except ObjectDoesNotExist:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('available_clubs')
            return redirect(url)

    def get_queryset(self):
        meeting = Meeting.objects.get(pk=self.kwargs.get('meeting_id'))
        subquery = meeting.get_members()
        return subquery

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        club = get_club_from_url_name(
            self.kwargs.get('club_url_name'))
        context = super().get_context_data(**kwargs)
        context['current_club'] = club
        context['current_user'] = self.request.user
        context['current_meeting'] = Meeting.objects.get(
            pk=self.kwargs.get('meeting_id'))
        context['moderators'] = club.get_moderators()
        context['members'] = club.get_members()

        return context
