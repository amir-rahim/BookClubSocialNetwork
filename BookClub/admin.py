from django.contrib import admin
from BookClub.models.user import User
from BookClub.models.club import Club

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
        'name','description', 'is_private', 'rules', 'created_on'
    ]
