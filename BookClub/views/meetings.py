"""Views for club meetings"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView
from BookClub.models import Meeting, Club, User
from django.contrib import messages
from django.shortcuts import redirect

class MeetingDetailsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View to display meeting details"""
    template_name = 'meeting_details.html'
    model = Meeting
    pk_url_kwarg = 'meeting_id'
    context_object_name = 'meeting'
    redirect_location='home' # should be meeting list

    # def get(self, request, *args, **kwargs):
    #     return redirect(self.redirect_location)
    
    # Redirect if club is private and user is not a member
    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name = self.kwargs['club_url_name'])
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
        #Override get_context_data for context other than meetings
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(club_url_name = self.kwargs['club_url_name'])
        context['user'] = self.request.user
        return context
