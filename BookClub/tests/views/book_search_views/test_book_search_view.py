

from django.test import RequestFactory, TestCase, tag
from django.urls import reverse
from BookClub.models.book import Book
from django.db.models import Q

from BookClub.models.user import User
from BookClub.views.async_views.book_search import BookSearchView
# testcases:
# select is none, select is something
# page is none, page is something
# query is none, query is something
# request is not ajax
# request is ajax - returns correct template
# get_template_names returns correct template depending on value of select
# page not an integer
# page emptypage


@tag('book_search', 'async')
class BookSearchTestCase(TestCase):

    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_books.json',
    ]

    def setUp(self):
        self.url = reverse('async_book_search')
        self.user = User.objects.get(pk=1)
        self.book1 = Book.objects.get(pk=1)
        self.rf = RequestFactory()

    def test_url(self):
        self.assertEqual(reverse('async_book_search'), '/search_books/')

    def test_select_is_set_get_templates(self):
        request = self.rf.get(self.url, data={'select': True})
        request.user = self.user

        view = BookSearchView()
        view.request = request
        self.assertEqual(view.get_template_names(), [
                         'partials/book_select_list.html'])

    def test_select_is_none_get_templates(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user

        view = BookSearchView()
        view.request = request
        self.assertEqual(view.get_template_names(), [
                         'partials/book_search_list.html'])

    def test_get_pagination_empty_list(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        paginate_by = 5
        object_list = []

        page_obj = view.get_pagination(object_list)
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 0)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_pagination_book_in_list(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        object_list = [self.book1]

        page_obj = view.get_pagination(object_list)
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_pagination_page_not_integer(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        object_list = [self.book1]

        page_obj = view.get_pagination(
            object_list=object_list, page="NotAnInteger")
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_pagination_page_empty_page(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        object_list = [self.book1]

        page_obj = view.get_pagination(
            object_list=object_list, page=100)
        self.assertEqual(page_obj.object_list, object_list)
        self.assertEqual(len(page_obj), 1)
        self.assertEqual(page_obj.number, 1)
        self.assertEqual(page_obj.has_next(), False)

    def test_get_queryset_query_is_none(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request

        object_list = view.get_queryset()
        self.assertEqual(len(object_list), Book.objects.all().count())

    def test_get_queryset_query_is_set(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        query = "book"
        object_list = view.get_queryset(query)
        self.assertEqual(len(object_list), Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(
                publisher__icontains=query)
        ).count())
        
    def test_get_select_is_set_paginate_by_is_set_to_5(self):
        request = self.rf.get(self.url, data={"select":"True"})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        view.get(request)
        self.assertTrue(view.paginate_by, 5)
        
    def test_get_select_is_none_paginate_by_is_set_to_20(self):
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        view.get(request)
        self.assertTrue(view.paginate_by, 20)
        
    def test_get_user_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        request = self.rf.get(self.url, data={})
        request.user = self.user
        view = BookSearchView()
        view.request = request
        view.get(request)
        self.assertTrue(view.paginate_by, 20)
