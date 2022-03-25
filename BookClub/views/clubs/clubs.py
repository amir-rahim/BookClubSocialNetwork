"""Club Related Views"""
from venv import create
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

from BookClub.forms import ClubForm
from BookClub.helpers import create_membership, get_club_from_url_name, has_membership_with_access, has_owner_rank
from BookClub.models import Club, ClubMembership, FeaturedBooks 
from BookClub.authentication_mixins import PrivateClubMixin


class CreateClubView(LoginRequiredMixin, CreateView):
    template_name = 'create_club.html'
    model = Club
    form_class = ClubForm

    def form_valid(self, form):
        response = super().form_valid(form)
        created_club = self.object
        create_membership(created_club, self.request.user, ClubMembership.UserRoles.OWNER)
        messages.success(self.request, 'Successfully created a new club!')
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)


class ClubDashboardView(LoginRequiredMixin, PrivateClubMixin, DetailView):
    template_name = "club_dashboard.html"
    model = Club
    slug_url_kwarg = 'club_url_name'
    slug_field = 'club_url_name'
    context_object_name = 'current_club'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = context['current_club'].get_club_owner()
        context['user'] = self.request.user
        context['featured_books'] = FeaturedBooks.objects.filter(club=context['current_club'])
        return context


class EditClubView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Club
    form_class = ClubForm
    template_name = 'edit_club.html'
    slug_url_kwarg = 'club_url_name'
    slug_field = 'club_url_name'
    context_object_name = 'club'

    def test_func(self):
        try:
            url_name = self.kwargs.get('club_url_name')
            club = get_club_from_url_name(url_name)
            if not has_owner_rank(self.request.user, club):
                messages.add_message(self.request, messages.ERROR, 'Access denied')
                return False
            else:
                return True
        except:
            messages.add_message(self.request, messages.ERROR, 'Club not found or you are not a member of this club')
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('club_dashboard', kwargs=self.kwargs)
            return redirect(url)