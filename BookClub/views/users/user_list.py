

from BookClub.models.user import User
from django.views.generic import ListView


class GlobalUserListView(ListView):
    paginate_by = 10
    model = User
    queryset = User.objects.all()
    template_name = "global_user_search.html"