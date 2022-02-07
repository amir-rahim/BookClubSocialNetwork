'''View for editing clubs'''
from django.conf import settings
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.helpers import RankRequiredMixin
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from BookClub.helpers import get_club_id
from django.conf import settings


class EditClubView(LoginRequiredMixin, DetailView, UpdateView):
    model = Club
    fields = ['name','description','rules','is_private']
    requiredRanking = ClubMembership.UserRoles.OWNER
    template_name = 'edit_club.html'
    
    def setup(self, request, *args, **kwargs):
        self.requiredClub = get_club_id(request)
        return super().setup(request, *args, **kwargs)
    
    def get_object(self):
        try:
            return Club.objects.get(pk=self.requiredClub)
        except:
            messages.add_message(self.request,messages.ERROR,'Club not found!')
            return None
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        try:
            club = Club.objects.get(pk=self.requiredClub)
            context['club'] = club
        except:
            return context
        return context
        
    def get_success_url(self):
        messages.add_message(self.request,messages.SUCCESS,'Club updated!')
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    
    #TODO: more testing