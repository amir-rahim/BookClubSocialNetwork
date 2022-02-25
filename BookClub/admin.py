from django.contrib import admin
from BookClub.models.user import User
from BookClub.models.club import Club
from BookClub.models.club_membership import ClubMembership
from BookClub.models.book import Book
from BookClub.models.meeting import Meeting

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'id','username', 'email'
    ]

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for clubs."""

    list_display = [
        'name','description', 'tagline', 'is_private', 'rules', 'created_on'
    ]

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club memberships."""

    list_display = [
        'club','user', 'membership', 'joined_on'
    ]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books ."""

    list_display = [
        'title', 'ISBN' , 'author' , 'publicationYear' ,'publisher'
    ]

@admin.register(Meeting)
class ClubMeetingAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""

    list_display = [
        'pk', 'organiser','club', 'meeting_time', 'created_on' ,'location' , 'title' , 'description' , 'type', 'book'
    ]



