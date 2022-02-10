"""User Related Views"""
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from BookClub.forms.user_forms import EditProfileForm, ChangePasswordForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from BookClub.helpers import LoginProhibitedMixin
from django.views.generic import FormView, TemplateView, UpdateView
from BookClub.models import User

class UserDashboardView(LoginRequiredMixin, TemplateView):
    """
    
    Class based view for user dashboard

    """
    model = User
    template_name = 'user_dashboard.html'
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(UserDashboardView, self).get_context_data(**kwargs)
        context['username'] = user.username
        context['email'] = user.email
        context['public_bio'] = user.public_bio
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    
    Class based view for editing user profile
    
    """
    model = User
    form_class = EditProfileForm
    template_name = 'edit_profile.html'

    def get(self, request, **kwargs):
        self.object = User.objects.get(username=self.request.user)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)
        
    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse('user_dashboard')

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)

        

class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    
    Class based view for changing user password
    
    """

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