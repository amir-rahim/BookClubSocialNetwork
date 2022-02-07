'''Club Related Views'''
from django.shortcuts import render

def club_dashboard(request):
    """This is the club dashboard view."""
    return render(request, 'club_dashboard.html')