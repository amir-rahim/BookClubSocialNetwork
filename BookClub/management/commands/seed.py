from django.core.management.base import BaseCommand
from faker import Faker
import random
from BookClub.models import User, Club, ClubMembership
from django.db.utils import IntegrityError

class Command(BaseCommand):
    """The database seeder."""

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        
    def add_arguments(self, parser):
        parser.add_argument('count', type=int, nargs='?', default=10)
    def generateUser():
        
        faker = Faker('en_GB')

        user = User.objects.create_user(
            username=faker.user_name(),
            email=faker.email(),
            public_bio="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
            password="Password123",
        )

        return user

    def handle(self, *args, **options):
        print("Seeding...")
        
        try:
            self.admin = User.objects.create_superuser(
                username='Admin',
                email='admin@example.org',
                public_bio=self.faker.text(max_nb_chars=200),
                password="Test123"
            )
        except IntegrityError:
            pass
        count = options.get('count', None)
        for i in range(count):
            print("Club: " + str(i+1))
            try:
                genOwner = Command.generateUser()
                    
                self.club = Club.objects.create(
                    name=self.faker.text(max_nb_chars=10),
                    description=self.faker.text(max_nb_chars=200), 
                    tagline=self.faker.text(max_nb_chars=30), 
                    rules=self.faker.text(max_nb_chars=30), 
                )
                
                self.club.add_owner(genOwner)
                #3 applicants/members
                    
                ran_member = random.randrange(10,15)
                ran_applicant = random.randrange(5,7)
                ran_moderator = random.randrange(1,3)
                
                for x in range (ran_applicant):
                    self.club.add_applicant(Command.generateUser())
                for y in range(ran_member):
                    self.club.add_member(Command.generateUser())
                #1 officer    
                for z in range(ran_moderator):
                    self.club.add_moderator(Command.generateUser())

            except IntegrityError as e:
                print("Integrity error was found, attempting again")
                print(str(e))