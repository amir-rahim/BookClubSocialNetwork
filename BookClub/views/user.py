'''User Related Views'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from BookClub.forms.user_forms import EditProfileForm, ChangePasswordForm
from django.contrib.auth import login
from django.contrib import messages

@login_required
def user_dashboard(request):
    """This is the user dashboard view."""
    return render(request, 'user_dashboard.html')

"""View of the change profile details page."""
@login_required
def edit_profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = EditProfileForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('user_dashboard')
    else:
        form = EditProfileForm(instance=current_user)
    return render(request, 'edit_profile.html', {'form': form})

"""View of the change password page."""
@login_required
def change_password(request):
    current_user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('dashboard')
    else:
        form = ChangePasswordForm()
    return render(request, 'password_change.html', {'form': form})