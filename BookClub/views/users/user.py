"""User Related Views"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, Q, OuterRef
from django.shortcuts import reverse
from django.views.generic import FormView, TemplateView, UpdateView

from BookClub.forms.user_forms import EditProfileForm, ChangePasswordForm
from BookClub.models import User, ClubMembership, Club, BookList
from BookClub.helpers import *


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """Class based view for user dashboard"""
    model = User
    template_name = 'user_dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(UserDashboardView, self).get_context_data(**kwargs)
        context['gravatar'] = user.gravatar
        context['username'] = user.username
        context['email'] = user.email
        context['public_bio'] = user.public_bio
        context['booklist_count'] = BookList.objects.filter(creator=user).count()
        context['club_count'] = ClubMembership.objects.filter(user=user).count()
        context['reputation'] = get_user_reputation(user)
        return context


class UserProfileView(LoginRequiredMixin, TemplateView):
    """Class based view for user profile"""
    model = User
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        user = User.objects.get(username=self.kwargs['username'])
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['gravatar'] = user.gravatar
        context['username'] = user.username
        context['public_bio'] = user.public_bio
        return context


class UserProfileMembershipsView(LoginRequiredMixin, TemplateView):
    """Class based view for user profile memberships"""
    model = Club
    template_name = 'user_profile_memberships.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs['username'])
        subquery = ClubMembership.objects.filter(user=user, club=OuterRef('pk'))
        clubs = Club.objects.filter(
            Q(Exists(subquery)) &
            ~Q(Exists(subquery.filter(membership=ClubMembership.UserRoles.APPLICANT)))
        )
        return clubs

    def get_context_data(self, **kwargs):
        user = User.objects.get(username=self.kwargs['username'])
        context = super().get_context_data(**kwargs)
        context['username'] = user.username
        context['public_bio'] = user.public_bio
        context['clubs'] = self.get_queryset()
        return context


class UserProfileFollowingView(LoginRequiredMixin, TemplateView):
    """Class based view for user profile following page"""
    model = User
    template_name = 'user_profile_following.html'

    def get_context_data(self, **kwargs):
        user = User.objects.get(username=self.kwargs['username'])
        context = super(UserProfileFollowingView, self).get_context_data(**kwargs)
        context['gravatar'] = user.gravatar
        context['username'] = user.username
        context['public_bio'] = user.public_bio
        context['following'] = list()  # to be updated with following when implemented
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Class based view for editing user profile"""
    model = User
    form_class = EditProfileForm
    template_name = 'edit_profile.html'

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse('user_dashboard')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """Class based view for changing user password"""
    form_class = ChangePasswordForm
    template_name = 'password_change.html'

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""
        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('user_dashboard')
