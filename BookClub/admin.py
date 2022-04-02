"""Configuration of the admin interface."""
from django.contrib import admin
from BookClub.models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Users."""

    list_display = [
        'id', 'username', 'email', 'public_bio'
    ]


@admin.register(UserToUserRelationship)
class UserToUserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for User to User Relationships."""

    list_display = [
        'source_user', 'target_user', 'relationship_type'
    ]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Clubs."""

    list_display = [
        'name', 'description', 'tagline', 'is_private', 'rules', 'created_on'
    ]


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Club Memberships."""

    list_display = [
        'club', 'user', 'membership', 'joined_on'
    ]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books."""

    list_display = [
        'id', 'title', 'ISBN', 'author', 'publicationYear', 'publisher'
    ]


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books Reviews."""

    list_display = [
        'book', 'creator', 'book_rating', 'title', 'created_on', 'content', 'rating'
    ]


@admin.register(BookReviewComment)
class BookReviewCommentAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books Review Comments."""

    list_display = [
        'book_review', 'creator', 'created_on', 'content', 'rating'
    ]


@admin.register(BookList)
class BookListAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books Lists."""

    list_display = [
        'title', 'creator', 'description', 'created_on'
    ]


@admin.register(Meeting)
class ClubMeetingAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Club Meetings."""

    list_display = [
        'organiser', 'club', 'meeting_time', 'created_on', 'location', 'title', 'description', 'type', 'book'
    ]


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Forums."""

    prepopulated_fields = {"slug": ("title",)}
    list_display = [
        'title', 'associated_with', 'slug'
    ]
    # filter_horizontal = ['posts']


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Forum Posts."""

    list_display = [
        'creator', 'created_on', 'forum', 'title', 'content', 'rating'
    ]


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Forum Comments."""

    list_display = [
        'creator', 'created_on', 'content', 'rating'
    ]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for voting."""

    list_display = [
        'creator', 'created_on', 'content_type', 'object_id', 'target'
    ]

@admin.register(BookShelf)
class BookShelfAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for the Bookshelf."""

    list_display = [
        'user', 'book', 'status'
    ]


@admin.register(FeaturedBooks)
class FeaturedBooksAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Featured Books."""

    list_display = [
        'club', 'book', 'reason'
    ]


@admin.register(UserRecommendations)
class UserRecAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for User Recommendations."""

    list_display = [
        'user', 'recommendations'
    ]
    
@admin.register(ClubRecommendations)
class ClubRecAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Club Recommendations."""
    
    list_display = [
        'club', 'recommendations'
    ]
