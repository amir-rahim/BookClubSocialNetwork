"""User related views."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, Q, OuterRef
from django.shortcuts import redirect, reverse
from django.views.generic import FormView, TemplateView, UpdateView, View

from BookClub.forms.user_forms import EditProfileForm, ChangePasswordForm
from BookClub.models import User, ClubMembership, Club, BookList, BookShelf
from BookClub.helpers import *
from BookClub.models.user2user import UserToUserRelationship


class UserDashboardView(LoginRequiredMixin, TemplateView):
    """View for the user dashboard."""
    model = User
    template_name = 'user/user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(UserDashboardView, self).get_context_data(**kwargs)
        if self.kwargs.get('username') is not None:
            user = User.objects.get(username=self.kwargs['username'])
            context['own_profile'] = False
            context['email'] = ''
        else:
            user = self.request.user
            context['own_profile'] = True
            context['email'] = user.email

        context['gravatar'] = user.gravatar
        context['username'] = user.username
        context['public_bio'] = user.public_bio
        context['booklist_count'] = BookList.objects.filter(creator=user).count()
        context['club_count'] = ClubMembership.objects.filter(user=user).count()
        context['reputation'] = get_user_reputation(user)
        context['number_of_to_read'] = BookShelf.get_to_read(user).count()
        context['number_of_reading'] = BookShelf.get_reading(user).count()
        context['number_of_on_hold'] = BookShelf.get_on_hold(user).count()
        context['number_of_completed'] = BookShelf.get_completed(user).count()
        context['number_of_following'] = UserToUserRelationship.objects.filter(source_user=user.id).count()
        return context


class UserProfileMembershipsView(LoginRequiredMixin, TemplateView):
    """List of another user's club memberships."""
    model = Club
    template_name = 'user/user_profile_memberships.html'
    context_object_name = 'posts'

    def get_queryset(self):
        """Get the other user's details from kwargs."""
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

class EditProfileView(LoginRequiredMixin, UpdateView):
    """Allow user to edit their profile."""
    model = User
    form_class = EditProfileForm
    template_name = 'user/edit_profile.html'

    def get_object(self):
        user = self.request.user
        return user

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse('user_dashboard')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    """Allow the user to change their password."""
    form_class = ChangePasswordForm
    template_name = 'user/password_change.html'

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
        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('user_dashboard')

class DeleteUserAccountView(LoginRequiredMixin, View):
    """Allow the user to permanently delete their account."""
    redirect_location = 'home'

    def action(self, user):
        user.delete()
        messages.success(self.request, "You have successfully deleted your account.")
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        self.action(user)

        return redirect(self.redirect_location)
    
    def get(self, request, *args, **kwargs):
        self.post(self, request, *args, **kwargs)
        return redirect(self.redirect_location)
