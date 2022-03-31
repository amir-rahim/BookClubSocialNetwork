from django.test import RequestFactory, TestCase, tag
from django.urls import reverse
from BookClub.models import Book, User, BookList, Club, ClubMembership
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from BookClub.views.async_views.async_search import SearchView
# testcases
# test club, user, booklist get_templates
# test book get_template and book select and book check
# test pagination


@tag('book_search','club_search','user_search','booklist_search', 'async')
class BookSearchTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
        'BookClub/tests/fixtures/booklists.json',
    ]

    def setUp(self):

        self.user = User.objects.get(pk=1)
        self.book1 = Book.objects.get(pk=1)
        self.rf = RequestFactory()
        self.booklist = BookList.objects.get(pk=1)
        self.bookcontenttype = ContentType.objects.get_for_model(Book)
        self.booklistcontenttype = ContentType.objects.get_for_model(BookList)
        self.clubcontenttype = ContentType.objects.get_for_model(Club)
        self.usercontenttype = ContentType.objects.get_for_model(User)
        self.url = reverse('async_search')
        self.bookdata = {
            'content_type' : self.bookcontenttype.pk
        }
        self.booklistdata = {
            'content_type' : self.booklistcontenttype.pk
        }
        self.clubdata = {
            'content_type' : self.clubcontenttype.pk
        }
        self.userdata = {
            'content_type' : self.usercontenttype.pk
        }

    def test_url(self):
        self.assertEqual(reverse('async_search'), '/search/')

    def test_select_is_set_get_templates(self):
        self.bookdata['select'] = True
        request = self.rf.get(self.url, data=self.bookdata)
        request.user = self.user

        view = SearchView()
        view.request = request
        self.assertEqual(view.get_template_names(self.bookcontenttype), [
                         'partials/book_select_list.html'])

    def test_select_is_none_get_templates(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user

        view = SearchView()
        view.request = request
        self.assertEqual(view.get_template_names(self.bookcontenttype), [
                         'partials/book_search_list.html'])

    def test_get_pagination_empty_list(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request
        paginate_by = 5
        object_list = []

        page_obj = view.get_pagination(object_list)
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 0)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_pagination_book_in_list(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request
        object_list = [self.book1]

        page_obj = view.get_pagination(object_list)
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_pagination_page_not_integer(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request
        object_list = [self.book1]

        page_obj = view.get_pagination(
            object_list=object_list, page="NotAnInteger")
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_pagination_page_empty_page(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request
        object_list = [self.book1]

        page_obj = view.get_pagination(
            object_list=object_list, page=100)
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_queryset_query_is_none(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request

        object_list = view.get_queryset("", self.bookcontenttype)
        self.assertEqual(len(object_list), Book.objects.all().count())

    def test_get_queryset_query_is_set(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request
        query = "book"
        object_list = view.get_queryset(query, self.bookcontenttype)
        self.assertEqual(len(object_list), Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(
                publisher__icontains=query)
        ).count())

    def test_get_select_is_set_paginate_by_is_set_to_5(self):
        self.bookdata['select'] = True
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request
        view.get(request)
        self.assertTrue(view.paginate_by, 5)

    def test_get_select_is_none_paginate_by_is_set_to_20(self):
        request = self.rf.get(
            self.url, data=self.bookdata)
        request.user = self.user
        view = SearchView()
        view.request = request
        view.get(request)
        self.assertTrue(view.paginate_by, 20)

    def test_get_user_logged_in(self):
        self.bookdata['query'] = ""
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, data=self.bookdata)
        self.assertContains(response, self.booklist.title)

    def test_get_user_anonymous(self):
        self.bookdata['query'] = ""
        response = self.client.get(self.url, data=self.bookdata)
        self.assertNotContains(response, self.booklist.title)

    def test_get_template_club(self):
        request = self.rf.get(self.url, data=self.clubdata)
        request.user = self.user

        view = SearchView()
        view.request = request
        self.assertEqual(view.get_template_names(self.clubcontenttype), [
                         'partials/club_search_list.html'])

    def test_get_template_user(self):
        request = self.rf.get(self.url, data=self.userdata)
        request.user = self.user

        view = SearchView()
        view.request = request
        self.assertEqual(view.get_template_names(self.usercontenttype), [
                         'partials/user_search_list.html'])

    def test_get_template_booklist(self):
        request = self.rf.get(self.url, data=self.booklistdata)
        request.user = self.user

        view = SearchView()
        view.request = request
        self.assertEqual(view.get_template_names(self.booklistcontenttype), [
                         'partials/booklist_search_list.html'])

    def test_get_template_book_check(self):
        self.bookdata['check'] = True
        request = self.rf.get(self.url, data=self.bookdata)
        request.user = self.user

        view = SearchView()
        view.request = request
        self.assertEqual(view.get_template_names(self.bookcontenttype), [
                         'partials/book_check_list.html'])

    def test_get_template_exception_raised_bad_argument(self):
        request = self.rf.get(self.url, data={'content_type' : 9999})
        request.user = self.user

        view = SearchView()
        view.request = request
        with self.assertRaises(Exception):
            view.get_template_names(ContentType.objects.get_for_model(ClubMembership))
