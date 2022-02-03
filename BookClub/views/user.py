'''User Related Views'''
from django.shortcuts import render

def user_dashboard(request):
    """This is the user dashboard view."""
    return render(request, 'user_dashboard.html')