'''Club Related Views'''
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from BookClub.models.club import Club
from BookClub.forms.club import ClubForm

from BookClub.models.club_membership import ClubMembership

def club_dashboard(request):
    """This is the club dashboard view."""
    return render(request, 'club_dashboard.html')

class CreateClubView(LoginRequiredMixin, CreateView):
    template_name = 'create_club.html'
    model = Club
    form_class = ClubForm
    success_url = reverse_lazy('home') # need to remove this attribute and amend 'get_absolute_url' method in Club model

    def form_valid(self, form):
        response = super().form_valid(form)
        created_club = self.object
        owner_membership = ClubMembership(user = self.request.user, club = created_club, membership = ClubMembership.UserRoles.OWNER)
        owner_membership.save()
        return response
