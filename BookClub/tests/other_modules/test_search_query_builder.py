from re import L
from BookClub.views.async_views.search_query_builder import *
from BookClub.models import Club, User,Book, BookList
from django.test import tag, TestCase


@tag('search','search_query_builder')
class TestSearchQueryAbstract(TestCase):
    
    def setUp(self):
        self.testQuery = SearchQuery(query="",q_objects=Q(), model = None)
        
    def test_query_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.testQuery.query()
    
    def test_match_type_error_undefined_match_models(self):
        with self.assertRaises(TypeError):
            self.testQuery.match()
            
    def test_match_matches_model_no_exclude(self):
        self.testQuery.match_models = (Club)
        self.testQuery.model = Club
        self.assertTrue(self.testQuery.match())
        
    def test_build_query_returns_unchanged_q_if_not_matched(self):
        newTestQuery = SearchQuery("", Q(Q.OR), User)
        newTestQuery.match_models = (Club)
        newTestQuery.model = User
        q = newTestQuery.build_query()
        self.assertEqual(q, Q(Q.OR))
    
        
        
    def test_match_matches_model_with_exclude(self):
        self.testQuery.match_models = (Club)
        self.testQuery.model = Club
        self.testQuery.exclude_models = (User)
        self.assertTrue(self.testQuery.match())
        
    def test_match_excludes_model_with_exclude(self):
        self.testQuery.match_models = (Club, User)
        self.testQuery.model = Club
        self.testQuery.exclude_models = Club
        self.assertFalse(self.testQuery.match())
        
    def test_match_matches_abstract_subclass(self):
        self.testQuery.match_models = (UserCreatedObject)
        self.testQuery.model = BookList
        self.assertTrue(self.testQuery.match())
        
@tag('search')
class BookQueryTestCase(TestCase):
    
    fixtures = ['BookClub/tests/fixtures/default_books.json']
    
    def setUp(self):
        self.book1 = Book.objects.get(pk=1)
        self.book2 = Book.objects.get(pk=2)
        self.q = BookQuery(query="", q_objects=Q(), model=Book)
        
    def test_empty_query_returns_all_books(self):
        query = self.q.build_query()
        allBooks = Book.objects.all()
        self.assertQuerysetEqual(Book.objects.filter(query), allBooks)
        
    def test_specific_query_returns_specific_book(self):
        self.q.query_string = self.book1.title
        query = self.q.build_query()
        book = Book.objects.filter((Q(title__icontains=self.book1.title) | Q(
            author__icontains=self.book1.title) | Q(publisher__icontains=self.book1.title)))
        self.assertQuerysetEqual(Book.objects.filter(query), book)
        
@tag('search')
class UserQueryTestCase(TestCase):
    
    fixtures = ['BookClub/tests/fixtures/default_users.json']
    
    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.q = UserQuery("", Q(), User)
        
    def test_empty_query_returns_all_users(self):
        query = self.q.build_query()
        allUsers = User.objects.all()
        self.assertQuerysetEqual(User.objects.filter(query), allUsers)
        
        
    def test_specific_query_returns_specific_user(self):
        self.q.query_string = self.user1.username
        query = self.q.build_query()
        user = User.objects.filter(Q(username__icontains=self.user1.username))
        self.assertQuerysetEqual(User.objects.filter(query), user)

@tag('search')
class BookListTestCase(TestCase):
    
    fixtures = ['BookClub/tests/fixtures/booklists.json', 'BookClub/tests/fixtures/default_users.json', 'BookClub/tests/fixtures/default_books.json']
    
    def setUp(self):
        self.booklist = BookList.objects.get(pk=1)
        self.q = BookListQuery("", Q(), BookList)
        
    def test_empty_query_returns_all(self):
        query = self.q.build_query()
        allLists =  BookList.objects.all()
        self.assertQuerysetEqual(BookList.objects.filter(query), allLists)
        
    def test_specific_query_returns_specific_list(self):
        self.q.query_string = self.booklist.title
        query = self.q.build_query()
        booklist = BookList.objects.filter(Q(title__icontains=self.booklist.title) | Q(description__icontains=self.booklist.title))
        self.assertQuerysetEqual(BookList.objects.filter(query), booklist)
        
        
@tag('search')
class ClubSearchTestCase(TestCase):
    
    fixtures = ['BookClub/tests/fixtures/default_clubs.json','BookClub/tests/fixtures/default_users.json','BookClub/tests/fixtures/default_memberships.json']
    
    def setUp(self):
        self.clubUserIsIn = Club.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.clubUserIsNotIn = Club.objects.get(pk=3)
        self.q = ClubQuery("", Q(), Club)
        
    def test_empty_query_returns_all_clubs_us_is_not_in(self):
        query = self.q.build_query(user=self.user)
        clubsUserIsNotIn = Club.objects.exclude(clubmembership__user__username=self.user.username)
        self.assertQuerysetEqual(clubsUserIsNotIn, Club.objects.filter(query))
        
    def test_specific_query_for_club_user_is_in_returns_empty_query_set(self):
        self.q.query_string = self.clubUserIsIn.name
        query = self.q.build_query(user=self.user)
        self.assertEqual(len(Club.objects.filter(query)), 0)
        
    def test_specific_query_for_club_user_is_not_in_returns_club(self):
        self.q.query_string = self.clubUserIsNotIn.name
        query = self.q.build_query(user=self.user)
        self.assertEqual(len(Club.objects.filter(query)), 1)
