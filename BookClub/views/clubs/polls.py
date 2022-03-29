"""Polls Related Views"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic import FormView

from BookClub.forms import PollForm
from BookClub.models import Club, ClubMembership


class CreateClubPollView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'clubs/create_club_poll.html'
    form_class = PollForm

    def test_func(self):
        user = self.request.user
        club = get_object_or_404(Club, club_url_name=self.kwargs['club_url_name'])
        try:
            membership = ClubMembership.objects.get(club=club, user=user)
        except Exception as e:
            return False

        return membership.membership > ClubMembership.UserRoles.MEMBER

    def form_valid(self, form):
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        form.save(club=club)
        messages.success(self.request, 'Successfully created a new poll for your club!')
        return redirect('club_dashboard', club_url_name=self.kwargs['club_url_name']) # replace with forum view or poll detail view

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form);

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['club'] = club
        return context
