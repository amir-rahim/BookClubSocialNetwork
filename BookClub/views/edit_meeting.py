from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from BookClub.forms.meeting_form import MeetingForm
from BookClub.models import *
from BookClub.forms.meeting_form import MeetingForm



class EditMeetingView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'edit_meeting.html'
    pk_url_kwarg = 'meeting_id'
    context_object_name = 'meeting'

    def test_func(self):
        try:
            meeting = self.get_object()
            
            club = meeting.get_club()
            organiser = meeting.get_organiser()
            rank = ClubMembership.objects.get(club=club, user=self.request.user)
            #The only people who can edit the meeting are the Owner (of the club) or the organiser.
            if(rank.membership != ClubMembership.UserRoles.OWNER or self.request.user != organiser):
                messages.add_message(self.request, messages.ERROR,'Access denied')
                return False
            else:
                return True
        except:
            messages.add_message(self.request, messages.ERROR,'Meeting not found or you are not a participant of this meeting')
            return False


    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Meeting updated!")
        #Need to change to whatever the meeting page is called 
        # return reverse('home', kwargs={'club_url_name':self.club_url_name})
        return reverse('home')

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('meetings_list', kwargs=self.kwargs)
            return redirect(url)

    def get_object(self):
        try:
            return super().get_object()
        except:
            messages.add_message(self.request,messages.ERROR,'Meeting not found!')
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        try:
            meeting = self.get_object()
            context['meeting'] = meeting
            context['id'] = meeting.id
        except:
            return context
        return context
