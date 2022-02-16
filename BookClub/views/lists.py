'''View for lists'''
from django.conf import settings
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from BookClub.helpers import *
from BookClub.models.user import User
from BookClub.models.club import *
from BookClub.models.club_membership import ClubMembership
from django.conf import settings


class MembersListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View to display member list"""

    template_name = 'club_members.html'

    # Redirect if club is private and user is not a member

    def test_func(self):
        try:
            current_club = Club.objects.get(url_name=self.kwargs['url_name'])
            if current_club.is_private and not current_club.is_member(self.request.user):
                messages.add_message(self.request, messages.ERROR, 'This club is private and you are not a member.')
                return False
            else:
                return True
        except:
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
        club = Club.objects.get(url_name=self.kwargs['url_name'])
        user = User.objects.get(id = self.request.user.id)
        try:
            rank = ClubMembership.objects.get(user=user, club=club)
        except:
            rank = None
        context['club'] = club
        context['members'] = club.get_members()
        context['moderators'] = club.get_moderators()
        context['owner'] = club.get_club_owner()
        context['request_user'] = rank

        return context
