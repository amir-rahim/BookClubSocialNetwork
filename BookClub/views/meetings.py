'''Meetings Related Views'''
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, View
from django.shortcuts import reverse, redirect
from BookClub.forms import MeetingForm
from BookClub.models import User, Club, ClubMembership, Meeting
from BookClub.helpers import *


class CreateMeetingView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    '''Class for club owners and moderators creating meetings for the club'''

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
