'''Authentication Related Views'''
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from BookClub.helpers import login_prohibited
from BookClub.forms import LogInForm, SignUpForm

@login_prohibited
def sign_up(request):
    """Manage sign up attempt."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            # The sign-up form is valid, we add the user to our database
            user = form.save()
            login(request, user)
            messages.success(request, "Successfully created account!")
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        
        messages.add_message(request, messages.ERROR, 'Unable to make account!')

    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})

@login_prohibited
def log_in(request):
    """Manage log in attempt."""
    if request.method == 'POST':
        form = LogInForm(request.POST)

        if form.is_valid():
            # Extract the input username and password and attempt to authenticate
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                # The user is authenticated, we then log-in the user and redirects it
                login(request, user)
                messages.success(request, ('Successfully Logged in!'))
                redirect_url = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
                return redirect(redirect_url)

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")

    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'login.html', {'form': form, 'next': next})
    


def log_out(request):
    """Redirect user to home page when they log out."""
    logout(request)
    messages.success(request, ('Successfully Logged Out!'))
    return redirect('home')