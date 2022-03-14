"""Club Related Views"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

from BookClub.forms import ClubForm
from BookClub.models import Club, ClubMembership


class CreateClubView(LoginRequiredMixin, CreateView):
    template_name = 'create_club.html'
    model = Club
    form_class = ClubForm

    def form_valid(self, form):
        response = super().form_valid(form)
        created_club = self.object
        owner_membership = ClubMembership(user=self.request.user, club=created_club,
                                          membership=ClubMembership.UserRoles.OWNER)
        owner_membership.save()
        messages.success(self.request, 'Successfully created a new club!')
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)


class ClubDashboardView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = "club_dashboard.html"
    model = Club
    slug_url_kwarg = 'club_url_name'
    slug_field = 'club_url_name'
    context_object_name = 'current_club'

    # Redirect if club is private and user is not a member
    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            if current_club.is_private and not current_club.is_member(self.request.user):
                messages.add_message(self.request, messages.ERROR, 'This club is private')
                return False
            else:
                return True
        except:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect('available_clubs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = context['current_club'].get_club_owner()
        context['user'] = self.request.user
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
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            rank = ClubMembership.objects.get(club=club, user=self.request.user)
            if rank.membership != ClubMembership.UserRoles.OWNER:
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

    def get_object(self):
        return super().get_object()
