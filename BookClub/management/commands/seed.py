from django.core.management.base import BaseCommand
from faker import Faker
import random
from BookClub.models import User, Club, ClubMembership, Book, BookReview, ForumPost, Forum, ForumComment
from django.db.utils import IntegrityError
from django.core.management import call_command


class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def add_arguments(self, parser):
        parser.add_argument('percent', type=int, nargs='?', default=10)

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
        call_command("importusers", percent)
        call_command("importbooksrandom", percent)
        call_command("importbookreviews")
        self.admin = User.objects.create_superuser(
            username='Admin',
            email='admin@example.org',
            public_bio=self.faker.text(max_nb_chars=200),
            password="Test123"
        )
        count = options.get('count', None)
        for i in range(count):
            print("Club: " + str(i + 1))
            try:
                self.create_club()

            except IntegrityError as e:
                print("Integrity error was found, skipping")
                print(str(e))
                continue
            
        id1 = Book.objects.all()[0].id
        self.add_reviews_to(id1)
        id2 = Book.objects.all()[1].id
        self.add_reviews_to(id2)

        self.create_global_forum()

    def create_club(self):
        genOwner = self.generateUser()
        name = self.faker.sentence(nb_words=1)
        club = Club.objects.create(
            name=name,
            club_url_name=Club.convertNameToUrl(None, name),
            description=self.faker.text(max_nb_chars=200),
            tagline=self.faker.text(max_nb_chars=30),
            rules=self.faker.text(max_nb_chars=30),
        )

        club.add_owner(genOwner)
        # 3 applicants/members

        ran_member = random.randrange(10, 15)
        ran_applicant = random.randrange(5, 7)
        ran_moderator = random.randrange(1, 3)

        for x in range(ran_applicant):
            club.add_applicant(self.generateUser())
        for y in range(ran_member):
            club.add_member(self.generateUser())
        # 1 officer
        for z in range(ran_moderator):
            club.add_moderator(self.generateUser())

    def add_reviews_to(self, pk):
        try:
            book = Book.objects.get(pk=pk)
        except:
            print("book not found")
            return

        for i in range(1, random.randrange(2, 20)):
            user = User.objects.order_by('?')[0]
            curReviews = BookReview.objects.filter(creator=user, book=book)
            while (curReviews.count() != 0):
                user = User.objects.order_by('?')[0]
                curReviews = BookReview.objects.filter(creator=user, book=book)

            if (curReviews.count() == 0):
                review = BookReview.objects.create(
                    creator=user,
                    book=book,
                    title="Book Title",
                    book_rating=random.randrange(0, 10),
                    content="Material Gworl"
                )

    def create_global_forum(self):
        globalForum = Forum.objects.create(title="Global Forum")

        for i in range(1, random.randrange(20, 35)):
            user = User.objects.order_by('?')[0]
            curPost = ForumPost.objects.create(
                title=self.faker.text(max_nb_chars=30),
                content=self.faker.text(max_nb_chars=1024),
                creator=user,
                forum=globalForum
            )
            # globalForum.add_post(curPost)
            for x in range(1, random.randrange(0, 5)):
                commentUser = User.objects.order_by('?')[0]
                curComment = ForumComment.objects.create(
                    content=self.faker.text(max_nb_chars=240),
                    creator=commentUser,
                    post=curPost
                )
