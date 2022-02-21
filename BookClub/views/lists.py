'''View for lists'''
from django.conf import settings
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.views.generic import TemplateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from BookClub.helpers import *
from BookClub.models.user import User
from BookClub.models.club import *
from BookClub.models.club_membership import ClubMembership
from BookClub.models.meeting import Meeting
from django.conf import settings


class MembersListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View to display member list"""

    template_name = 'club_members.html'

    # Redirect if club is private and user is not a member

    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            if current_club.is_private and not current_club.is_member(self.request.user):
                messages.add_message(self.request, messages.ERROR, 'This club is private and you are not a member.')
                return False
            else:
                return True
        except:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('club_dashboard', kwargs=self.kwargs)
            return redirect(url)

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        user = User.objects.get(id = self.request.user.id)
        try:
            rank = ClubMembership.objects.get(user=user, club=club)
        except:
            rank = None
        context['club'] = club
        context['members'] = club.get_members()
        context['moderators'] = club.get_moderators()
        context['owner'] = club.get_club_owner()
        context['request_user'] = rank

        return context

class ApplicantListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """View to display applicant list"""

    template_name = 'applicant_list.html'

    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            if not current_club.is_moderator(self.request.user) and not current_club.is_owner(self.request.user):
                messages.add_message(self.request, messages.ERROR, 'Only Owners and Moderators can view this.')
                return False
            else:
                return True
        except:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('club_dashboard', kwargs=self.kwargs)
            return redirect(url)

    def get_context_data(self, **kwargs):
        """Generate context data to be shown in the template."""

        context = super().get_context_data(**kwargs)
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        user = User.objects.get(id = self.request.user.id)
        try:
            rank = ClubMembership.objects.get(user=user, club=club)
        except:
            rank = None
        context['club'] = club
        context['applicants'] = club.get_applicants()
        context['moderators'] = club.get_moderators()
        context['owner'] = club.get_club_owner()
        context['request_user'] = rank

        return context
    
class MeetingListView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    """View to display meeting list"""

    template_name = 'club_meetings.html'
    context_object_name = 'meetings'
    
    def test_func(self):
        try:
            current_club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            current_user = self.request.user
            rank = ClubMembership.objects.get(user = current_user, club = current_club)
            if rank.membership == ClubMembership.UserRoles.APPLICANT:
                messages.add_message(self.request, messages.ERROR, 'You must be a member of this club to view meetings.')
                return False
            else:
                return True
        except:
            return False

    def get_queryset(self):
        club = Club.objects.get(club_url_name = self.kwargs.get('club_url_name'))
        subquery = Meeting.objects.filter(club=club)
        return subquery
        
    def get_context_data(self, **kwargs):
        #Override get_context_data for context other than meetings
        context = super().get_context_data(**kwargs)
        context['club'] = Club.objects.get(club_url_name = self.kwargs.get('club_url_name'))
        return context
    

