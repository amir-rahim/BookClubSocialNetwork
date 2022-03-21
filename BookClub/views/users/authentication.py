"""Authentication Related Views"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, reverse
from django.views.generic import FormView, View
from verify_email.email_handler import send_verification_email

from BookClub.forms import LogInForm, SignUpForm
from BookClub.authentication_mixins import LoginProhibitedMixin


class SignUpView(LoginProhibitedMixin, FormView):
    """View class for handling user sign-ups"""
    form_class = SignUpForm
    template_name = 'sign_up.html'
    redirect_when_logged_in_url = 'home'

    def form_valid(self, form):
        inactive_user = send_verification_email(self.request, form)
        messages.add_message(self.request, messages.SUCCESS, "A verification link has been sent to your email to complete your registration.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The credentials provided were invalid!")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(self.redirect_when_logged_in_url)


class LogInView(LoginProhibitedMixin, FormView):
    """
        View class for handling logging the user in and setting the club_id session key
    """
    form_class = LogInForm
    template_name = 'login.html'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        # if the user exists, log them in and set the clubId value for the session
        if user is not None:
            # The user is authenticated, we then log-in the user and redirects it
            login(self.request, user)
            messages.success(self.request, ('Successfully Logged in!'))
            redirect_url = settings.REDIRECT_URL_WHEN_LOGGED_IN
            return redirect(redirect_url)
        else:
            messages.add_message(self.request, messages.ERROR, "The credentials provided were invalid!")
            return render(self.request, 'login.html')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The credentials provided were incomplete!")
        return super().form_invalid(form);


class LogOutView(LoginRequiredMixin, View):
    """

        Class that handles logging a user out.

    """

    def get(self, request):
        logout(request)
        return redirect('home')
