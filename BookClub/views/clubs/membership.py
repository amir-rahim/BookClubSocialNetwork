"""Memberships related views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, Q, OuterRef
from django.views.generic import ListView

from BookClub.models import Club, ClubMembership


class AvailableClubsView(LoginRequiredMixin, ListView):
    """Render a list of clubs the current user is not in."""
    model = Club
    template_name = 'clubs/available_clubs.html'
    context_object_name = 'clubs'
    paginate_by=10

    def get_queryset(self):
        subquery = ClubMembership.objects.filter(user=self.request.user.pk, club=OuterRef('pk'))
        clubs = Club.objects.filter(
            ~Q(Exists(subquery)) |
            Q(Exists(subquery.filter(membership=ClubMembership.UserRoles.APPLICANT)))
        )
        return clubs


class MyClubMembershipsView(LoginRequiredMixin, ListView):
    """Render a table of clubs the user is a member of."""
    model = Club
    template_name = 'clubs/my_club_memberships.html'
    context_object_name = 'posts'

    def get_queryset(self):
        subquery = ClubMembership.objects.filter(user=self.request.user.pk, club=OuterRef('pk'))
        clubs = Club.objects.filter(
            Q(Exists(subquery)) &
            ~Q(Exists(subquery.filter(membership=ClubMembership.UserRoles.APPLICANT)))
        )
        return clubs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = self.get_queryset()
        return context

class ApplicationListView(LoginRequiredMixin, ListView):
    """Render a list of private clubs the user has applied to join."""
    model = Club
    template_name = 'clubs/applications_list.html'
    context_object_name = 'clubs'

    def get_queryset(self):
        subquery = ClubMembership.objects.filter(user=self.request.user.pk, club=OuterRef('pk'))
        clubs = Club.objects.filter(
            Q(Exists(subquery.filter(membership=ClubMembership.UserRoles.APPLICANT)))
        )
        return clubs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = self.get_queryset()
        return context