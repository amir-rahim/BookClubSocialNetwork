"""User list related views."""
from BookClub.models.user import User
from django.views.generic import ListView


class GlobalUserListView(ListView):
    """Search all users site wide."""
    paginate_by = 10
    model = User
    queryset = User.objects.all()
    template_name = "user/global_user_search.html"