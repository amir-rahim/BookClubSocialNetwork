from django.contrib import admin
from BookClub.models import *
from BookClub.models.forum import ForumPost


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'id', 'username', 'email'
    ]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for clubs."""

    list_display = [
        'name', 'description', 'tagline', 'is_private', 'rules', 'created_on'
    ]


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club memberships."""

    list_display = [
        'club', 'user', 'membership', 'joined_on'
    ]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books ."""

    list_display = [
        'title', 'ISBN', 'author', 'publicationYear', 'publisher'
    ]


@admin.register(BookReview)
class BookReview(admin.ModelAdmin):
    """Configuration of the admin interface for Books Reviews ."""

    list_display = [
        'book', 'user', 'rating', 'review', 'createdOn'
    ]


@admin.register(Meeting)
class ClubMeetingAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""

    list_display = [
        'organiser', 'club', 'meeting_time', 'created_on', 'location', 'title', 'description', 'type', 'book'
    ]


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""
    list_display = [
        'creator', 'created_on', 'title', 'content', 'rating'
    ]


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""
    prepopulated_fields = {"slug": ("title",)}
    list_display = [
        'title', 'associatedWith', 'slug'
    ]
    filter_horizontal = ['posts']


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""

    list_display = [
        'creator', 'created_on', 'content', 'rating']
    filter_horizontal = ['subComments']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""

    list_display = [
        'creator', 'created_on', 'content_type', 'object_id', 'target'
    ]
