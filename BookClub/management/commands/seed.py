from subprocess import call
from django.core.management.base import BaseCommand
from faker import Faker
import random

import pytz
from BookClub.models import *
from django.db.utils import IntegrityError
from django.core.management import call_command
from randomtimestamp import randomtimestamp
from datetime import timedelta


class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def add_arguments(self, parser):
        parser.add_argument('percent', type=int, nargs='?', default=10)

        parser.add_argument('--count', '--c', type=int, default=5)
        
        parser.add_argument('--deploy', action="store_true")

        parser.add_argument(
            '--load',
            action='store_true',
            help='Load from csv',
        )

        parser.add_argument(
            '--admin',
            action='store_true',
            help='Add admin superuser',
        )

    def generateUser(self):
        faker = Faker('en_GB')

        user = User.objects.create_user(
            username=faker.user_name(),
            email=faker.email(),
            public_bio="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
                       "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
                       "laboris nisi ut aliquip ex ea commodo consequat.",
            password="Password123",
        )

        return user

    def handle(self, *args, **options):
        print("Seeding...")
        percent = options.get('percent', 1)
        if options['load']:
            call_command("importusers", percent)
            call_command("importbooksrandom", percent)
            call_command("importbookreviews")
            
        elif options['deploy']:
            call_command("importusers", "--deploy")
            call_command("importbooksrandom","--deploy")
            call_command("importbookreviews")
        else:
            for i in range(0, 150):
                self.generateUser()
                
            call_command("importbooksrandom", "--deploy")
        try:
            self.admin = User.objects.create_superuser(
                username='Admin',
                email='admin@example.org',
                public_bio=self.faker.text(max_nb_chars=200),
                password="Test123"
            )
        except Exception:
            pass
        
        count = options.get('count', 5)
        for i in range(count):
            print("Club: " + str(i + 1))
            try:
                self.create_club()

            except IntegrityError as e:
                print("Integrity error was found, skipping")
                print(str(e))
                continue

        self.create_global_forum()
        self.add_books_to_shelf()
        self.add_following()
        self.create_booklists()
        self.add_reviews()
        
    def add_reviews(self):
        count = BookReview.objects.all().count()
        
        if count < 300:
            i = count
            while i < 300:
                book = Book.objects.order_by('?')[0]
                if self.add_review_to_book(book):
                    i +=1
                
    def add_review_to_book(self, book):
        u = self.get_random_user()
        try:
            review = BookReview.objects.create(creator=u, book=book,book_rating=random.randrange(0,10), title=self.faker.text(max_nb_chars=30), content=self.faker.text(max_nb_chars=120))
            for x in range(1, random.randrange(0, 5)):
                commentUser = User.objects.order_by('?')[0]
                curComment = BookReviewComment.objects.create(
                    content=self.faker.text(max_nb_chars=240),
                    creator=commentUser,
                    book_review = review
                )
                self.add_votes_public(curComment)
            
            return True
        except:
            return False

    def create_club(self):
        owner = User.objects.order_by('?')[0]
        name = self.faker.sentence(nb_words=1)
        privacy = random.getrandbits(1)
        club = Club.objects.create(
            name=name,
            club_url_name=Club.convertNameToUrl(None, name),
            is_private=privacy,
            description=self.faker.text(max_nb_chars=200),
            tagline=self.faker.text(max_nb_chars=30),
            rules=self.faker.text(max_nb_chars=30),
        )

        club.add_owner(owner)
        # 3 applicants/members

        ran_member = random.randrange(10, 15)
        ran_applicant = random.randrange(5, 7)
        ran_moderator = random.randrange(1, 3)
        if(privacy):
            for x in range(ran_applicant):
                club.add_applicant(self.get_random_user())
        for y in range(ran_member):
            club.add_member(self.get_random_user())
        # 1 officer
        for z in range(ran_moderator):
            club.add_moderator(self.get_random_user())

        self.add_to_club_forum(club)
        self.add_meetings(club)
        self.feature_book(club)

    def add_to_club_forum(self, club):
        forum = Forum.objects.get(associated_with=club)
        for i in range(1, random.randrange(20, 35)):
            user = User.objects.filter(
                clubmembership__club=club).order_by('?')[0]
            curPost = ForumPost.objects.create(
                title=self.faker.text(max_nb_chars=30),
                content=self.faker.text(max_nb_chars=1024),
                creator=user,
                forum=forum
            )
            self.add_votes_private(curPost, club)
            for x in range(1, random.randrange(0, 5)):
                commentUser = User.objects.filter(
                    clubmembership__club=club).order_by('?')[0]
                curComment = ForumComment.objects.create(
                    content=self.faker.text(max_nb_chars=240),
                    creator=commentUser,
                    post=curPost
                )
                self.add_votes_private(curComment, club)

    def add_meetings(self, club):
        owner = User.objects.get(
            clubmembership__club=club, clubmembership__membership=ClubMembership.UserRoles.OWNER)
        for i in range(0, 4):
            meeting_time = randomtimestamp(start_year=2021, end_year=2022)
            meeting_end_time = meeting_time + \
                timedelta(minutes=random.randint(30, 75))
            meeting_time = pytz.utc.localize(meeting_time)
            meeting_end_time = pytz.utc.localize(meeting_end_time)
            type = random.choices(Meeting.MeetingType.choices)
            book = None
            if(type[0] == ('B','Book')):
                book = Book.objects.order_by('?')[0]
            m = Meeting.objects.create(meeting_time=meeting_time, meeting_end_time=meeting_end_time,
                                   organiser=owner, club=club, location=self.faker.text(max_nb_chars=30), title=self.faker.text(max_nb_chars=60), description=self.faker.text(max_nb_chars=200), type=type[0][0], book=book)
            for i in range(0, 10):
                user = self.get_random_user_from_club(club)
                m.join_member(user)
                
    def feature_book(self,club):
        feature = FeaturedBooks.objects.create(club=club, book=Book.objects.order_by('?')[0], reason=self.faker.text(max_nb_chars=50))
        
    def add_books_to_shelf(self):
        for i in range (0, 50):
            user = self.get_random_user()
            for x in range(1, 3):
                book = Book.objects.order_by('?')[0]
                status = random.choice(BookShelf.ListType.choices)
                BookShelf.objects.create(user=user, book=book, status=status[0])
            

    def get_random_user(self):
        return User.objects.order_by('?')[0]
    
    def get_random_user_from_club(self, club):
        return User.objects.filter(clubmembership__club=club).order_by('?')[0]
    
    def create_global_forum(self):

        globalForum = Forum.objects.get_or_create(title="Global Forum")[0]
        for i in range(0, random.randrange(20, 35)):
            user = User.objects.order_by('?')[0]
            curPost = ForumPost.objects.create(
                title=self.faker.text(max_nb_chars=30),
                content=self.faker.text(max_nb_chars=1024),
                creator=user,
                forum=globalForum
            )
            self.add_votes_public(curPost)
            for x in range(1, random.randrange(0, 5)):
                commentUser = User.objects.order_by('?')[0]
                curComment = ForumComment.objects.create(
                    content=self.faker.text(max_nb_chars=240),
                    creator=commentUser,
                    post=curPost
                )
                self.add_votes_public(curComment)
                
    def add_following(self):
        for i in (0,random.randrange(30, 50)):
            user = self.get_random_user()
            for x in range(2,4):
                other = self.get_random_user()
                if user != other:
                    UserToUserRelationship.objects.create(source_user=user, target_user=other, relationship_type=1)
    
    def add_votes_public(self, content):
        for i in (0,random.randrange(0, 7)):
            user = self.get_random_user()
            type = random.getrandbits(1)
            con = ContentType.objects.get_for_model(content.__class__)
            id = content.id
            try:
                Vote.objects.create(type=type, content_type=con, object_id=id, creator=user)
            except IntegrityError:
                continue
            
    def add_votes_private(self, content, club):
        for i in (0,random.randrange(0, 7)):
            user = self.get_random_user_from_club(club)
            type = random.getrandbits(1)
            con = ContentType.objects.get_for_model(content.__class__)
            id = content.id
            try:
                Vote.objects.create(
                    type=type, content_type=con, object_id=id, creator=user)
            except IntegrityError:
                continue
            
    def create_booklists(self):
        for i in (0,random.randrange(10, 20)):
            user = self.get_random_user()
            b = BookList.objects.create(creator=user,title=self.faker.text(max_nb_chars=120), description=self.faker.text(max_nb_chars=240))
            for x in (0,random.randrange(3, 30)):
                book = Book.objects.order_by('?')[0]
                b.add_book(book)
