from django.contrib import admin
from BookClub.models import *
from BookClub.models.forum import ForumPost



@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'id', 'username', 'email'
    ]


@admin.register(UserToUserRelationship)
class UserToUserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for User to User relationships."""

    list_display = [
        'source_user', 'target_user', 'relationship_type'
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
        'id', 'title', 'ISBN', 'author', 'publicationYear', 'publisher'
    ]


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books Reviews ."""

    list_display = [
        'book', 'creator', 'book_rating' , 'title' , 'created_on','content'
    ]

@admin.register(BookReviewComment)
class BookReviewCommentAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books Review Comments ."""

    list_display = [
        'book_review','creator','created_on','content'
    ]


@admin.register(BookList)
class BookListAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Books Reviews ."""

    list_display = [
        'title', 'creator', 'description', 'created_on'
    ]


@admin.register(Meeting)
class ClubMeetingAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""

    list_display = [
        'organiser', 'club', 'meeting_time', 'created_on', 'location', 'title', 'description', 'type', 'book'
    ]


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""
    prepopulated_fields = {"slug": ("title",)}
    list_display = [
        'title', 'associated_with', 'slug'
    ]
    # filter_horizontal = ['posts']


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""
    list_display = [
        'creator', 'created_on', 'forum', 'title', 'content', 'rating'
    ]


@admin.register(ForumComment)
class ForumCommentAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""

    list_display = [
        'creator', 'created_on', 'content', 'rating'
    ]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club meetings."""

    list_display = [
        'creator', 'created_on', 'content_type', 'object_id', 'target'
    ]

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for club polls."""

    list_display = [
        'club', 'title', 'deadline', 'created_on', 'active'
    ]

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for poll options."""

    list_display = [
        'poll', 'text', 'book'
    ]

@admin.register(BookShelf)
class BookShelfAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for Book Shelf."""

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

    list_display = [
        'user', 'recommendations'
    ]
    
@admin.register(ClubRecommendations)
class ClubRecAdmin(admin.ModelAdmin):
    
    list_display = [
        'club', 'recommendations'
                    ]
