from enum import Enum
from BookClub.helpers import get_memberships_with_access
from BookClub.models import Book, User, Club, Meeting, BookList, ClubMembership, TextPost, TextComment, UserCreatedObject, ForumPost, ForumComment
from django.db.models import Q, Model
from BookClub.models.forum import Forum


class SearchQuery():

    """
        Abstract base class for creating search queries with.
        Set the class to match using match_models, then define a custom query to add to our q object in query.
    """
    model = None
    match_models = None
    exclude_models = None
    q_objects = None
    query_string = ""

    def __init__(self, query, q_objects, model):
        self.q_objects = q_objects
        self.query_string = query
        self.model = model

    def build_query(self, **kwargs):
        if self.match(**kwargs):
            return self.query(**kwargs)
        return self.q_objects

    def query(self, **kwargs):
        raise NotImplementedError(
            "Trying to use abstract base method. You need to create an implementation of match yourself before you can use it!")

    def match(self, **kwargs):
        if self.match_models is None:
            raise TypeError("Error, match models is undefined")
        if self.exclude_models is None:
            return issubclass(self.model, self.match_models)
        return issubclass(self.model, self.match_models) and not issubclass(self.model, self.exclude_models)


class BookQuery(SearchQuery):

    match_models = Book

    def query(self, **kwargs):
        self.q_objects.add((Q(title__icontains=self.query_string) | Q(
            author__icontains=self.query_string) | Q(publisher__icontains=self.query_string)), Q.OR)
        return self.q_objects

class BookListQuery(SearchQuery):

    match_models = BookList

    def query(self, **kwargs):
        self.q_objects.add(data=(Q(title__icontains=self.query_string) | Q(description__icontains=self.query_string)), conn_type=Q.OR)
        return self.q_objects


class ClubQuery(SearchQuery):

    match_models = Club

    def query(self, **kwargs):
        user = kwargs.get('user', None)
        user_clubs = get_memberships_with_access(user)
        self.q_objects.add(Q(name__icontains=self.query_string) & ~Q(pk__in=user_clubs), Q.OR)
        self.q_objects.add(Q(description__icontains=self.query_string) & ~Q(pk__in=user_clubs), Q.OR)
        self.q_objects.add(Q(tagline__icontains=self.query_string)
                           & ~Q(pk__in=user_clubs), Q.OR)
        return self.q_objects


class UserQuery(SearchQuery):

    match_models = User

    def query(self, **kwargs):
        self.q_objects.add(Q(username__icontains=self.query_string), Q.OR)
        return self.q_objects
