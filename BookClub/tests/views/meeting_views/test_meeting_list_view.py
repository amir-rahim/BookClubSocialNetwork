from django.test import TestCase, tag
from django.urls import reverse

from BookClub.models import User, Club, ClubMembership, Meeting, Book


@tag('meeting', 'meeting_list')
class MeetingListTest(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_meetings.json',
        'BookClub/tests/fixtures/default_books.json'
    ]

    def setUp(self):
        self.club = Club.objects.get(pk=1)
        self.meeting = Meeting.objects.get(pk=1, club=self.club)
        self.book = Book.objects.get(pk=1)
        self.url = reverse("meeting_list", kwargs={'club_url_name': self.club.club_url_name})
        self.owner = User.objects.get(username="johndoe")
        self.moderator = User.objects.get(username="janedoe")
        self.member = User.objects.get(username="jackdoe")
        self.applicant = User.objects.get(username="sebdoe")
        ClubMembership.objects.create(user = self.owner, club = self.club, membership = ClubMembership.UserRoles.OWNER)
        ClubMembership.objects.create(user = self.moderator, club = self.club, membership = ClubMembership.UserRoles.MODERATOR)
        ClubMembership.objects.create(user = self.member, club = self.club, membership = ClubMembership.UserRoles.MEMBER)
        ClubMembership.objects.create(user = self.applicant, club = self.club, membership = ClubMembership.UserRoles.APPLICANT)

    def test_url(self):
        url = f'/club/{self.club.club_url_name}/meetings/'
        self.assertEqual(self.url, url)

    def test_get_template_logged_in(self):
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_applicant_cannot_see_meeting_list(self):
        self.client.login(username=self.applicant.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateNotUsed(response, 'club_meetings.html')

    """Testing to see what information is displayed"""

    def test_owner_can_see_meeting_information(self):
        self.client.login(username=self.owner.username, password="Password123")
        self.meeting.leave_member(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response, 'Book meeting 1')
        self.assertContains(response, 'Feb. 22, 2022, 7 p.m.')
        self.assertContains(response, 'johndoe')
        meetings = list(response.context['meetings'])
        self.assertEqual(len(meetings), 6)

    def test_moderator_can_see_meeting_information(self):
        self.client.login(username=self.moderator.username, password="Password123")
        self.meeting.leave_member(self.moderator)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response, 'Book meeting 1')
        self.assertContains(response, 'Feb. 22, 2022, 7 p.m.')
        self.assertContains(response, 'johndoe')
        meetings = list(response.context['meetings'])
        self.assertEqual(len(meetings), 6)

    def test_member_can_see_meeting_information(self):
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response, 'Book meeting 1')
        self.assertContains(response, 'Feb. 22, 2022, 7 p.m.')
        self.assertContains(response, 'johndoe')
        meetings = list(response.context['meetings'])
        self.assertEqual(len(meetings), 6)

    def test_allowed_user_can_see_multiple_meetings(self):
        self.meeting3 = Meeting.objects.create(
            organiser=self.member,
            club=self.club,
            meeting_time="2022-02-22T21:00+00:00",
            meeting_end_time="2022-02-22T22:00+00:00",
            created_on="2022-02-10",
            location="Franklin Wilkins Library GS05",
            title="Book meeting 3",
            description="This is a book meeting",
            type="B",
            book=self.book
        )
        self.client.login(username=self.owner.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')

        self.assertContains(response, 'Book meeting 1')
        self.assertContains(response, 'johndoe')
        self.assertContains(response, 'Feb. 22, 2022, 7 p.m.')

        self.assertContains(response, 'Book meeting 3')
        self.assertContains(response, 'jackdoe')
        self.assertContains(response, 'Feb. 22, 2022, 9 p.m.')

        meetings = list(response.context['meetings'])
        self.assertEqual(len(meetings), 7)

    def test_allowed_user_can_see_join_button(self):
        self.client.login(username=self.owner.username, password="Password123")
        club = Club.objects.get(pk=2)
        ClubMembership.objects.create(user=self.owner, club=club, membership=ClubMembership.UserRoles.MEMBER)
        response = self.client.get(reverse("meeting_list", kwargs={'club_url_name': club.club_url_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response, 'Join Meeting')

    def test_allowed_user_can_see_leave_button(self):
        self.client.login(username=self.owner.username, password="Password123")
        meeting = Meeting.objects.get(pk=3)
        club = Club.objects.get(pk=2)
        ClubMembership.objects.create(user=self.owner, club=club, membership=ClubMembership.UserRoles.MEMBER)
        meeting.join_member(self.owner)
        response = self.client.get(reverse("meeting_list", kwargs={'club_url_name': club.club_url_name}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_meetings.html')
        self.assertContains(response, 'Leave Meeting')

    def test_invalid_club(self):
        self.client.login(username=self.member.username, password="Password123")
        response = self.client.get(reverse("meeting_list", kwargs={"club_url_name": 'fakeclub'}))
        self.assertRedirects(response, expected_url=reverse("club_dashboard", kwargs={"club_url_name": 'fakeclub'}), status_code=302, target_status_code=302)
