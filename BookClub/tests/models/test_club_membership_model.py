from django.core.exceptions import ValidationError
from django.test import TestCase, tag

from BookClub.models import User, Club, ClubMembership


@tag('models', 'memberships')
class ClubMembershipModelTestCase(TestCase):
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_owners.json',
    ]

    def setUp(self):
        self.users = []
        self.users.append(User.objects.get(pk=1))

        self.clubs = []
        self.clubs.append(Club.objects.get(pk=1))

        self.club_memberships = []
        self.club_memberships.append(ClubMembership.objects.get(pk=1))

    def _set_second_user(self):
        self.users.append(User.objects.get(pk=2))

    def _set_second_club(self):
        self.clubs.append(Club.objects.get(pk=2))

    def _create_extra_membership(self, user_index, club_index, membership_level):
        club_membership = ClubMembership(
            user=self.users[user_index],
            club=self.clubs[club_index],
            membership=membership_level
        )
        club_membership.save()
        self.club_memberships.append(club_membership)

    def _assert_membership_is_valid(self, membership_index):
        try:
            self.club_memberships[membership_index].full_clean()
        except(ValidationError):
            self.fail('Test club membership should be valid')

    def _assert_membership_is_invalid(self, membership_index):
        with self.assertRaises(Exception):
            self.club_memberships[membership_index].full_clean()

    def test_valid_club_membership(self):
        self._assert_membership_is_valid(0)

    def test_user_can_only_have_one_membership_per_club(self):
        self._set_second_user()
        self._set_second_club()
        self._create_extra_membership(1, 0, ClubMembership.UserRoles.MODERATOR)

        self.club_memberships[0].user = self.club_memberships[1].user
        self.club_memberships[0].club = self.club_memberships[1].club

        self._assert_membership_is_invalid(0)

    def test_user_cannot_be_null(self):
        self.club_memberships[0].user = None
        self._assert_membership_is_invalid(0)

    def test_membership_is_deleted_when_user_is_deleted(self):
        self.users[0].delete()
        self.assertEqual(len(ClubMembership.objects.filter(user=self.users[0])), 0)

    def test_user_can_be_a_member_in_multiple_clubs(self):
        self._set_second_club()
        self._create_extra_membership(0, 1, ClubMembership.UserRoles.MEMBER)
        self._assert_membership_is_valid(1)

    def test_club_cannot_be_null(self):
        self.club_memberships[0].club = None
        self._assert_membership_is_invalid(0)

    def test_membership_is_deleted_when_club_is_deleted(self):
        self.clubs[0].delete()
        self.assertEqual(len(ClubMembership.objects.filter(club=self.clubs[0])), 0)

    def test_club_can_have_multiple_members(self):
        self._set_second_user()
        self._create_extra_membership(1, 0, ClubMembership.UserRoles.MEMBER)
        self._assert_membership_is_valid(1)

    def test_membership_must_have_valid_membership_level(self):
        self.club_memberships[0].membership = 3
        self._assert_membership_is_invalid(0)

    def test_membership_level_cannot_be_blank(self):
        self.club_memberships[0].membership = None
        self._assert_membership_is_invalid(0)

    def test_club_can_only_have_one_owner(self):
        self.club_memberships[0].membership = ClubMembership.UserRoles.OWNER
        self.club_memberships[0].save()
        self._set_second_user()
        self._create_extra_membership(1, 0, ClubMembership.UserRoles.MODERATOR)
        self.club_memberships[1].membership = ClubMembership.UserRoles.OWNER
        self._assert_membership_is_invalid(1)
