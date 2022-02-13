'''Memberships Related Views'''
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.models.club_membership import ClubMembership
from BookClub.models.club import Club
from django.db.models import Exists, Q, OuterRef

class AvailableClubsView(LoginRequiredMixin, ListView):
    model = Club
    template_name = 'available_clubs.html'
    context_object_name = 'posts'

    def get_queryset(self):
        subquery = ClubMembership.objects.filter(user=self.request.user.pk, club=OuterRef('pk'))
        clubs = Club.objects.filter(
            ~Q(Exists(subquery)) |
            Q(Exists(subquery.filter(membership=ClubMembership.UserRoles.APPLICANT)))
        )
        return clubs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clubs'] = self.get_queryset()
        return context

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
        

