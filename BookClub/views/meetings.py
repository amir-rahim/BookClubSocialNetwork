'''Meetings Related Views'''
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView
from django.shortcuts import reverse, redirect
from django.urls import reverse_lazy
from BookClub.forms.meeting import MeetingForm
from BookClub.models.club import Club
from BookClub.models.user import User
from BookClub.models.club_membership import ClubMembership
from BookClub.models.meeting import Meeting
from BookClub.helpers import *


class CreateMeetingView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'create_meeting.html'
    model = Meeting
    form_class = MeetingForm
    success_url = '/'

    # Redirect if user is not a moderator or owner of the club
    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            if not (has_owner_rank(self.request.user, current_club) or has_moderator_rank(self.request.user, current_club)):
                messages.add_message(self.request, messages.ERROR, 'You are not allowed to create meetings!')
                return False
            else:
                return True
        except:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect('club_dashboard', self.kwargs['club_url_name'])

    def form_valid(self, form):
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        form.instance.organiser = self.request.user
        form.instance.club = club
        form.save()
        form.instance.join_member(self.request.user)
        messages.success(self.request, ('Successfully created a new meeting!'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form);

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['current_club'] = club
        return context
