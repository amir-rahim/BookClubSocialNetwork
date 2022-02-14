'''View for editing clubs'''
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from BookClub.helpers import RankRequiredMixin
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from django.conf import settings


class EditClubView(LoginRequiredMixin, UserPassesTestMixin, DetailView, UpdateView):
    model = Club
    fields = ['name','description','rules','is_private']
    template_name = 'edit_club.html'
    permission_denied_message = "Access denied"
    raise_exception = False
    
    def test_func(self):
        try:
            club = Club.objects.get(url_name=self.kwargs['url_name'])
            rank = ClubMembership.objects.get(club=club, user=self.request.user)
            if(rank.membership != ClubMembership.UserRoles.OWNER):
                messages.add_message(self.request, messages.ERROR,'Access denied')
                return False
            else:
                return True
        except:
            messages.add_message(self.request, messages.ERROR,'Club not found or you are not a member of this club')
            return False
         
        
    
    def get_object(self):
        try:
            return Club.objects.get(url_name=self.kwargs['url_name'])
        except:
            messages.add_message(self.request,messages.ERROR,'Club not found!')
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        try:
            club = Club.objects.get(url_name=self.kwargs['url_name'])
            context['club'] = club
        except:
            return context
        return context
        
    def get_success_url(self):
        messages.add_message(self.request,messages.SUCCESS,'Club updated!')
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    
    #TODO: more testing