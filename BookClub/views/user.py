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
        
    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse('user_dashboard')

class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    
    Class based view for changing user password
    
    """
    model = User
    form_class = ChangePasswordForm
    template_name = 'password_change.html'

    def form_valid(self, form):
        new_password = form.cleaned_data.get('new_password')
        self.request.user.set_password(new_password)
        login(self.request, self.request.user)
        return super().form_valid(form)
        
    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "One of these fields are invalid")
        return super().form_invalid(form)
    
    def get_success_url(self):
        return reverse('user_dashboard')

# @login_required
# def user_dashboard(request):
#     """This is the user dashboard view."""
#     return render(request, 'user_dashboard.html')

# """View of the change profile details page."""
# @login_required
# def edit_profile(request):
#     current_user = request.user
#     if request.method == 'POST':
#         form = EditProfileForm(instance=current_user, data=request.POST)
#         if form.is_valid():
#             messages.add_message(request, messages.SUCCESS, "Profile updated!")
#             form.save()
#             return redirect('user_dashboard')
#     else:
#         form = EditProfileForm(instance=current_user)
#     return render(request, 'edit_profile.html', {'form': form})

# """View of the change password page."""
# @login_required
# def change_password(request):
#     current_user = request.user
#     if request.method == 'POST':
#         form = ChangePasswordForm(data=request.POST)
#         if form.is_valid():
#             password = form.cleaned_data.get('password')
#             if check_password(password, current_user.password):
#                 new_password = form.cleaned_data.get('new_password')
#                 current_user.set_password(new_password)
#                 current_user.save()
#                 login(request, current_user)
#                 messages.add_message(request, messages.SUCCESS, "Password updated!")
#                 return redirect('user_dashboard')
#     else:
#         form = ChangePasswordForm()
#     return render(request, 'password_change.html', {'form': form})