'''Static Related Views'''
from django.shortcuts import render

from BookClub.helpers import login_prohibited

@login_prohibited
def home(request):
    """This is the home view of the application."""
    return render(request, 'home.html')