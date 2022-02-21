from django.db import IntegrityError, models
from BookClub.models import User, Club, Book

class Meeting(models.Model):
    class MeetingType(models.TextChoices):
        BOOK = 'B'
        CLUB = 'C'
        SOCIAL = 'S'
        OTHER = 'O'

    organiser = models.ForeignKey(User, related_name='meeting_organiser', blank = False, on_delete = models.CASCADE)
    club = models.ForeignKey(Club, blank = False, on_delete = models.CASCADE)
    meeting_time = models.DateTimeField(blank = False)
    created_on = models.DateField(auto_now_add = True, editable = False)
    location = models.CharField(max_length = 120, blank = True)
    title = models.CharField(max_length = 120, blank = False)
    description = models.CharField(max_length = 250, blank = False)
    members = models.ManyToManyField(User, related_name='meeting_attendees')
    type = models.CharField(max_length=1, choices = MeetingType.choices, blank = False)
    book = models.ForeignKey(Book, blank = True, null = True, on_delete = models.CASCADE)


    def __str__(self):
        return self.title

    def get_organiser(self):
        return self.organiser

    def get_club(self):
        return self.club

    def get_meeting_time(self):
        return self.meeting_time

    def get_created_on(self):
        return self.created_on
    
    def get_location(self):
        return self.location

    def get_title(self):
        return self.title
    
    def get_description(self):
        return self.description

    def get_members(self):
        return self.members.all()

    def get_type(self):
        return self.type

    def get_book(self):
        return self.book

    def get_number_of_attendants(self):
        return self.members.count()

    def join_member(self, member):
        if not self.members.filter(username = member.username).exists():
            self.members.add(member)
            self.save()

    def leave_member(self, member):
        if self.members.filter(username = member.username).exists():
            self.members.remove(member)
            self.save()


    