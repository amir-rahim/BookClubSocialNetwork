'''View for lists'''
from django.conf import settings
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.helpers import *
from BookClub.models.club import *
from BookClub.models.club_membership import ClubMembership
from BookClub.helpers import get_club_id
from django.conf import settings


class MembersListView(RankRequiredMixin, TemplateView):
    """View to display member list"""
    template_name = 'members_list.html'

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        club = Club.objects.get(pk=get_club_id(request))
        context['club_id'] = club
        context['members'] = get_members(club)
        context['moderators'] = get_moderators(club)
        context['owners'] = get_owners(club)

        return context
