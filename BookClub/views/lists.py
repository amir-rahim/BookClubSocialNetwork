'''View for lists'''
from django.conf import settings
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from BookClub.helpers import *
from BookClub.models.club import *
from BookClub.models.club_membership import ClubMembership
from django.conf import settings


class MembersListView(LoginRequiredMixin, TemplateView):
    """View to display member list"""
    
    template_name = 'club_members.html'

    # Redirect if club is private and user is not a member
    def get(self, request, *args, **kwargs):
        current_club = Club.objects.get(url_name=self.kwargs['url_name'])
        if current_club.is_private:
            if not current_club.is_member(request.user):
                messages.add_message(request, messages.ERROR, 'This club is private and you are not a member.')
                return redirect('available_clubs')
        return render(request, 'club_members.html', context=self.get_context_data(**kwargs))
    
    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""
    
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(url_name=self.kwargs['url_name'])
        context['club'] = club
        context['members'] = club.get_members()
        context['moderators'] = club.get_moderators()
        context['owner'] = club.get_club_owner()

        return context
