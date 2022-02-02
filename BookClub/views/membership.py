'''Memberships Related Views'''
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def available_clubs(request):
    pass
