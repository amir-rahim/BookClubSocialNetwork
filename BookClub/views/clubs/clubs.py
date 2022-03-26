"""Club Related Views"""
from venv import create
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView

from BookClub.forms import ClubForm
from BookClub.helpers import create_membership, get_club_from_url_name, has_membership_with_access, has_owner_rank, get_club_reputation, has_member_rank, has_moderator_rank
from BookClub.models import Club, ClubMembership, FeaturedBooks, Book
from BookClub.forms.club import FeatureBookForm
from BookClub.authentication_mixins import PrivateClubMixin


class CreateClubView(LoginRequiredMixin, CreateView):
    template_name = 'create_club.html'
    model = Club
    form_class = ClubForm

    def form_valid(self, form):
        response = super().form_valid(form)
        created_club = self.object
        create_membership(created_club, self.request.user, ClubMembership.UserRoles.OWNER)
        messages.success(self.request, 'Successfully created a new club!')
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "The data provided was invalid!")
        return super().form_invalid(form)


class ClubDashboardView(LoginRequiredMixin, PrivateClubMixin, DetailView):
    template_name = "club_dashboard.html"
    model = Club
    slug_url_kwarg = 'club_url_name'
    slug_field = 'club_url_name'
    context_object_name = 'current_club'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_club = context['current_club']
        user = self.request.user

        context['owner'] = context['current_club'].get_club_owner()
        context['user'] = self.request.user
        context['featured_books'] = FeaturedBooks.objects.filter(club=context['current_club'])
        context['reputation'] = get_club_reputation(context['current_club'])
        context['featured_replacement_range'] = range(5 - context['featured_books'].count())
        context['can_edit_featured'] = current_club.is_owner(user) or current_club.is_moderator(user)
        return context


class EditClubView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Club
    form_class = ClubForm
    template_name = 'edit_club.html'
    slug_url_kwarg = 'club_url_name'
    slug_field = 'club_url_name'
    context_object_name = 'club'

    def test_func(self):
        try:
            url_name = self.kwargs.get('club_url_name')
            club = get_club_from_url_name(url_name)
            if not has_owner_rank(self.request.user, club):
                messages.add_message(self.request, messages.ERROR, 'Access denied')
                return False
            else:
                return True
        except:
            messages.add_message(self.request, messages.ERROR, 'Club not found or you are not a member of this club')
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            url = reverse('club_dashboard', kwargs=self.kwargs)
            return redirect(url)


class FeatureBookView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'edit_featured_books.html'
    model = FeaturedBooks
    form_class = FeatureBookForm

    # Redirect if user is not a moderator or owner of the club
    def test_func(self):
        try:
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            if not (has_owner_rank(self.request.user, club) or has_moderator_rank(self.request.user, club)):
                if club.is_private == False or has_member_rank(self.request.user, club):
                    messages.error(self.request, 'Only the owner or a moderator can feature books!')
                    return False
                else:
                    return False
            else:
                return True
        except ObjectDoesNotExist:
            messages.error(self.request, 'Club not found or you are not a member of this club')
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super(LoginRequiredMixin, self).handle_no_permission()
        else:
            return redirect('club_dashboard', self.kwargs['club_url_name'])

    def form_valid(self, form):
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        if FeaturedBooks.objects.filter(book = self.request.POST.get("book")).exists():
            messages.error(self.request, 'Book is already featured!')
            return super().form_invalid(form)
        featuredBook = form.save(commit=False)
        featuredBook.club = club
        messages.success(self.request, 'Successfully featured book!')
        return super(FeatureBookView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "The data provided was invalid!")
        return super().form_invalid(form)

    def get_success_url(self):
        # Change to redirect to list of meetings
        return reverse('club_dashboard', kwargs={'club_url_name': self.kwargs['club_url_name']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
        context['current_club'] = club
        context['featured_books'] = FeaturedBooks.objects.filter(club=context['current_club'])
        return context

class RemoveFeaturedBookView(LoginRequiredMixin, View):
    redirect_location = 'club_dashboard'

    # Redirect if user is not a moderator or owner of the club

    def is_actionable(self, current_user, club, book):
        return (has_owner_rank(current_user, club) or has_moderator_rank(current_user, club)) and (FeaturedBooks.objects.filter(club=club, book=book).exists())

    def is_not_actionable(self):
        messages.error(self.request, f"You are not allowed to edit this!")

    def action(self, featured):
        featured.delete()
        messages.success(self.request, "You have removed the book from featured.")

    def post(self, request, *args, **kwargs):
        try:
            book = Book.objects.get(id=self.kwargs['book_id'])
            club = Club.objects.get(club_url_name=self.kwargs['club_url_name'])
            featured = FeaturedBooks.objects.get(club=club, book=book)
            current_user = self.request.user
        except:
            messages.error(self.request, "Error, invalid data.")
            return redirect(self.redirect_location, kwargs['club_url_name'])

        if self.is_actionable(current_user, club, book):
            self.action(featured)
        else:
            self.is_not_actionable()

        return redirect(self.redirect_location, kwargs['club_url_name'])

    def get(self, request, *args, **kwargs):
        return redirect(self.redirect_location, kwargs['club_url_name'])
