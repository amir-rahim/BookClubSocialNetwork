


from django.forms import ValidationError
from django.test import TestCase
from BookClub.models import Club, User, ClubMembership
from django.db import IntegrityError, transaction
class AddUserTestCase(TestCase):
    
    fixtures = [
        'BookClub/tests/fixtures/default_users.json',
        'BookClub/tests/fixtures/default_clubs.json',
        'BookClub/tests/fixtures/default_club_owners.json',
        ]

    def setUp(self):
        self.club1 = Club.objects.get(pk = 1)
        self.club2 = Club.objects.get(pk = 2)
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.testUser = User.objects.create(
            username="Dave",
            email="davestation@davestation.com",
            public_bio = "I am dave yognaut and I have the pants",
            password="Password123",
        )
    def _assert_club_is_valid(self):
        try:
            self.club1.full_clean()
        except(ValidationError):
            self.fail('Test club should be valid')

    def _assert_club_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.club1.full_clean()

    def test_valid_club(self):
        self._assert_club_is_valid()
        
    def testAddUserValidInfo(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.add_user(self.testUser, ClubMembership.UserRoles.MEMBER)
        membershipAfter = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipBefore+1, membershipAfter)
        userMembership = ClubMembership.objects.get(user=self.testUser, club=self.club1)
        self.assertEqual(userMembership.membership, ClubMembership.UserRoles.MEMBER)
        
    def testAddUserInvalidInfo(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.add_user(self.testUser, ClubMembership.UserRoles.MEMBER)
        membershipAfter = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipBefore+1, membershipAfter)
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        try:
            with transaction.atomic():
                self.club1.add_user(self.testUser, ClubMembership.UserRoles.MEMBER)
        except IntegrityError:
            pass
        membershipAfterDuplicateAdd = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipAfter, membershipAfterDuplicateAdd)
        
    def testAddOwnerAlreadyExists(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.add_owner(self.testUser)
        membershipAfter = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipBefore, membershipAfter)
        
    def testAddOwnerNoOwnerExists(self):
        testClub = Club.objects.create(name="Test",description="testclub",rules="test",tagline="tagline", is_private=False)
        membershipBefore = ClubMembership.objects.filter(club=testClub).count()
        testClub.add_owner(self.testUser)
        membershipAfter = ClubMembership.objects.filter(club=testClub).count()
        self.assertEqual(membershipBefore+1, membershipAfter)
        userMembership = ClubMembership.objects.get(user=self.testUser, club=testClub)
        self.assertEqual(userMembership.membership, ClubMembership.UserRoles.OWNER)
        
    def testAddMember(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.add_member(self.testUser)
        membershipAfter = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipBefore+1, membershipAfter)
        userMembership = ClubMembership.objects.get(user=self.testUser, club=self.club1)
        self.assertEqual(userMembership.membership, ClubMembership.UserRoles.MEMBER)
        
    def testAddModerator(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.add_moderator(self.testUser)
        membershipAfter = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipBefore+1, membershipAfter)
        userMembership = ClubMembership.objects.get(user=self.testUser, club=self.club1)
        self.assertEqual(userMembership.membership, ClubMembership.UserRoles.MODERATOR)
        
    def testAddApplicant(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.add_applicant(self.testUser)
        membershipAfter = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipBefore+1, membershipAfter)
        userMembership = ClubMembership.objects.get(user=self.testUser, club=self.club1)
        self.assertEqual(userMembership.membership, ClubMembership.UserRoles.APPLICANT)
        
    def testRemoveMember(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.add_user(self.testUser, ClubMembership.UserRoles.MEMBER)
        membershipAfter = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipBefore+1, membershipAfter)
        self.club1.remove_from_club(self.testUser)
        membershipAfterRemoval = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipAfterRemoval, membershipBefore)
        
    def testRemoveMemberNotInClub(self):
        membershipBefore = ClubMembership.objects.filter(club=self.club1).count()
        self.club1.remove_from_club(self.testUser)
        membershipAfterRemoval = ClubMembership.objects.filter(club=self.club1).count()
        self.assertEqual(membershipAfterRemoval, membershipBefore)
        
        
    
