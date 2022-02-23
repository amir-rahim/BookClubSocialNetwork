'''Meetings Related Views'''
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.shortcuts import reverse, redirect
from django.urls import reverse_lazy
from BookClub.forms.meeting import MeetingForm
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
        # meeting = form.save(commit=False)
        form.instance.organiser = self.request.user
        form.instance.club = club
        form.instance.save()
        form.instance.join_member(self.request.user)
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
