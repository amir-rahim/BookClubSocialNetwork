"""Edit meeting related views."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView

from BookClub.forms.meeting import MeetingForm
from BookClub.models import Meeting, User
from BookClub.models.club_membership import ClubMembership


class EditMeetingView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow the organiser of a meeting or the owner of a club to edit the details of a given meeting."""
    model = Meeting
    form_class = MeetingForm
    template_name = 'meeting/edit_meeting.html'
    pk_url_kwarg = 'meeting_id'

    def test_func(self):
        """Check the current user is the owner of the club or the organiser of the meeting."""
        try:
            meeting = self.get_object()
            club = meeting.get_club()
            organiser = meeting.get_organiser()
            rank = ClubMembership.objects.get(club=club, user=self.request.user)
            # The only people who can edit the meeting are the Owner (of the club) or the organiser.
            if rank.membership != ClubMembership.UserRoles.OWNER and rank.membership != ClubMembership.UserRoles.MODERATOR and self.request.user != organiser:
                messages.add_message(self.request, messages.ERROR, 'Access denied')
                return False
            return True
        except:
            messages.add_message(self.request, messages.ERROR,
                                 'Meeting not found or you are not a participant of this meeting')
            return False

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Meeting updated!")
        return reverse('meeting_details', kwargs=self.kwargs)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('meeting_list', kwargs={'club_url_name': self.kwargs['club_url_name']})
            return redirect(url)

    def get_object(self):
        try:
            return super().get_object()
        except:
            messages.add_message(self.request, messages.ERROR, 'Meeting not found!')
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        meeting = self.get_object()
        context['meeting'] = meeting
        context['id'] = meeting.id
        context['club'] = meeting.get_club()
        context['members'] = meeting.members.all()
        return context


class RemoveMeetingMember(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Allow the organiser of the meeting or the owner of a club to remove participants of a meeting."""
    model = Meeting
    pk_url_kwarg = 'meeting_id'
    http_method_names = ['post']

    def test_func(self):
        """Check if the user is the organiser of the meeting or the owner of the club."""
        try:
            meeting = self.get_object()
            club = meeting.get_club()
            organiser = meeting.get_organiser()
            rank = ClubMembership.objects.get(
                club=club, user=self.request.user)
            # The only people who can edit the meeting are the Owner (of the club) or the organiser.
            if rank.membership != ClubMembership.UserRoles.OWNER and rank.membership != ClubMembership.UserRoles.MODERATOR and self.request.user != organiser:
                messages.add_message(
                    self.request, messages.ERROR, 'Access denied')
                return False

            return True
        except:
            messages.add_message(self.request, messages.ERROR,
                                 'Meeting not found or you are not a participant of this meeting')
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()

        url = reverse('meeting_list', kwargs={'club_url_name': self.kwargs['club_url_name']})
        return redirect(url)

    def post(self, request, *args, **kwargs):
        try:
            meeting = self.get_object()
            user = User.objects.get(username=self.request.POST.get('user'))
        except:
            messages.error(request, "User not found!")
            return redirect(reverse('meeting_details', kwargs=kwargs))

        if meeting.organiser.id is not user.id:
            meeting.members.remove(user)
            meeting.save()
            return redirect(reverse('edit_meeting', kwargs=kwargs))
        else:
            messages.error(request, "Cannot kick organiser!")
            return redirect(reverse('meeting_details', kwargs=kwargs))
