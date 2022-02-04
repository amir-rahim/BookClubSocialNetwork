from django.views.generic import DeleteView
from django.views.generic.detail import SingleObjectMixin


class Delete_Club_View(DeleteView,SingleObjectMixin):
    pass
