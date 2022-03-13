"""Static Related Views"""
from django.shortcuts import render

def home(request):
    """This is the home view of the application."""
    return render(request, 'home.html')