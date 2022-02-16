"""Library Related Views"""
from django.shortcuts import render


def library_dashboard(request):
    """This is the library dashboard view."""
    return render(request, 'library_dashboard.html')
