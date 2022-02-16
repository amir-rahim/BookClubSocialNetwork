'''Club Related Views'''
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from BookClub.models.club import Club, User
from BookClub.forms.club import ClubForm

from BookClub.models.club_membership import ClubMembership

class CreateClubView(LoginRequiredMixin, CreateView):
    template_name = 'create_club.html'
    model = Club
    form_class = ClubForm
    # success_url = reverse_lazy('home') # need to remove this attribute and amend 'get_absolute_url' method in Club model

    def form_valid(self, form):
        response = super().form_valid(form)
        created_club = self.object
        owner_membership = ClubMembership(user = self.request.user, club = created_club, membership = ClubMembership.UserRoles.OWNER)
        owner_membership.save()
        messages.success(self.request, ('Successfully created a new club!'))
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form);



class ClubDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "club_dashboard.html"

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
        current_club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['current_club'] = current_club
        context['owner'] = current_club.get_club_owner()
        context['user'] = self.request.user
        return context
