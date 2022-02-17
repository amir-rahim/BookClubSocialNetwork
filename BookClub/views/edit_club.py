'''View for editing clubs'''
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from BookClub.models.club import Club
from BookClub.forms.club import ClubForm
from BookClub.models.club_membership import ClubMembership
from django.conf import settings


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
            if(rank.membership != ClubMembership.UserRoles.OWNER):
                messages.add_message(self.request, messages.ERROR,'Access denied')
                return False
            else:
                return True
        except:
            messages.add_message(self.request, messages.ERROR,'Club not found or you are not a member of this club')
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('club_dashboard', kwargs=self.kwargs)
            return redirect(url)
    
    def get_object(self):
        try:
            return super().get_object()
        except:
            messages.add_message(self.request,messages.ERROR,'Club not found!')
            return None

    # def get_success_url(self):
    #     messages.add_message(self.request,messages.SUCCESS,'Club updated!')
    #     print('got to success url')
    #     return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    #TODO: more testing