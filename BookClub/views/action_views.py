from django.views.generic import TemplateView
from BookClub.models.club import Club, User
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ActionView(TemplateView):
    
    redirect_location = reverse('home')
    
    def get(self, club, user, request, *args, **kwargs):
        """
        Handle get request

        Args:
            request (Django Request): The request we have recieved
        """
        try:
            club = Club.objects.get(pk=club);
            currentUser = request.user
            targetUser = User.objects.get(pk=user)
        except:
            messages.error(request, "Error, user or club not found")
            
        if(self.is_actionable(currentUser, targetUser, club)):
            self.action(currentUser, targetUser, club)
        
        return redirect(self.redirect_location)
    
    def is_actionable(currentUser, targetUser, club):
        raise NotImplementedError("This method isn't implented yet.")
    
    def action(currentUser, targetUser, club):
        raise NotImplementedError("This method isn't implemented yet.")