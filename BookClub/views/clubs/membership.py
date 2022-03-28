"""Memberships Related Views"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, Q, OuterRef
from django.views.generic import ListView

from BookClub.models import Club, ClubMembership


class AvailableClubsView(LoginRequiredMixin, ListView):
    model = Club
    template_name = 'available_clubs.html'
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
    model = Club
    template_name = 'my_club_memberships.html'
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
    model = Club
    template_name = 'applications_list.html'
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