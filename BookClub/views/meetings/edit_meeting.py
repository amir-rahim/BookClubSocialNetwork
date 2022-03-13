from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView

from BookClub.forms.meeting_form import MeetingForm
from BookClub.models import Meeting, User
from BookClub.models.club_membership import ClubMembership


class EditMeetingView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'edit_meeting.html'
    pk_url_kwarg = 'meeting_id'

    def test_func(self):
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
        # Need to change to whatever the meeting page is called
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
        try:
            meeting = self.get_object()
            context['meeting'] = meeting
            context['id'] = meeting.id
            context['club'] = meeting.get_club()
            context['members'] = meeting.members.all()
        except:
            return context
        return context


class RemoveMeetingMember(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Meeting
    pk_url_kwarg = 'meeting_id'
    http_method_names = ['post']

    def test_func(self):
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
        meeting = self.get_object()
        user = self.kwargs.get('member_id')
        if user is not None and meeting is not None:
            user = User.objects.get(pk=user)
            if meeting.organiser is not user:
                meeting.members.remove(user)
                meeting.save()
                kwargs.pop('member_id')
                return redirect(reverse('edit_meeting', kwargs=kwargs))
            else:
                kwargs.pop('member_id')
                messages.error(request, "Cannot kick organiser!")
                return redirect(reverse('meeting_details', kwargs=kwargs))

        else:
            kwargs.pop('member_id')
            messages.error(request, "User not found!")
            return redirect(reverse('meeting_details', kwargs=kwargs))
