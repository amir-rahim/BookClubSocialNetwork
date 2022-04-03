"""Meeting model."""
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError


from BookClub.models import User, Club, Book


class Meeting(models.Model):
    """Meeting model allowing Users to create events in a Club.

    Attributes:
        organiser: The User that created the Meeting.
        club: The Club the Meeting is made in.
        meeting_time: The Date Time that the Meeting is being held at.
        meeting_end_time: The Date Time that the Meeting ends at.
        created_on: The Date the Meeting was created on.
        location: A string containing the location of the Meeting.
        title: A string containing the title of the Meeting.
        description: A string containing the description of the Meeting.
        members: A list of Users that are attending the Meeting.
        type: The MeetingType specifying the type of Meeting.
        book: The Book the Meeting may be associated with.
    """
    class Meta:
        ordering=['-meeting_time']
    class MeetingType(models.TextChoices):
        """Attributes a type to the Meeting."""
        BOOK = 'B'
        CLUB = 'C'
        SOCIAL = 'S'
        OTHER = 'O'

    organiser = models.ForeignKey(User, related_name='meeting_organiser', blank=False, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, blank=False, on_delete=models.CASCADE)
    meeting_time = models.DateTimeField(blank=False)
    meeting_end_time = models.DateTimeField(blank=False)
    created_on = models.DateField(auto_now_add=True, editable=False)
    location = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=120, blank=False)
    description = models.CharField(max_length=250, blank=False)
    members = models.ManyToManyField(User, related_name='meeting_attendees')
    type = models.CharField(max_length=1, choices=MeetingType.choices, blank=False)
    book = models.ForeignKey(Book, blank=True, null=True, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('meeting_details', kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': self.pk})

    def get_delete_url(self):
        return reverse('delete_meeting', kwargs={'club_url_name': self.club.club_url_name, 'meeting_id': self.pk})

    def __str__(self):
        return self.title

    def get_delete_str(self):
        end_time_str = self.meeting_end_time.strftime("%H:%M") if self.meeting_end_time.date() == self.meeting_time.date() else self.meeting_end_time.strftime("%A %-d %b %Y, %H:%M")
        return f'a {self.get_type_name()} meeting of "{str(self.club)}" club on {self.meeting_time.strftime("%A %-d %b %Y, %H:%M")} - {end_time_str}'

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

    def get_type_name(self):
        type_names = {
            'B': 'Book',
            'C': 'Club',
            'S': 'Social',
            'O': '"Other" type'
        }
        return type_names[self.type]

    def get_book(self):
        return self.book

    def get_number_of_attendants(self):
        return self.members.count()

    def join_member(self, member):
        if not self.members.filter(username=member.username).exists():
            self.members.add(member)
            self.save()

    def leave_member(self, member):
        if self.members.filter(username=member.username).exists():
            self.members.remove(member)
            self.save()

    def get_is_not_past(self):
        return timezone.now() < self.meeting_time
