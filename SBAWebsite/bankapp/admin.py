from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, NewsArticle, CannedMessageCategory, CannedMessage, AdvisorClientPairing
)

class AdvisorClientPairingAdmin(admin.ModelAdmin):
    """
    Admin interface for Advisor-Client Pairing.
    - Allows manual assignment of advisors to existing clients.
    - Keeps the admin interface clean and maintainable.
    """
    list_display = ['client', 'advisor']
    list_filter = ['advisor']
    search_fields = ['client__email', 'advisor__email']

admin.site.register(AdvisorClientPairing, AdvisorClientPairingAdmin)

class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin:
    - Allows role editing for all users, including superusers.
    - Ensures changes are saved correctly without affecting other users.
    """
    model = User
    list_display = ['email', 'username', 'role', 'is_superuser', 'is_active']
    list_filter = ['role', 'is_superuser', 'is_active']
    ordering = ['email']
    search_fields = ['email', 'username']

    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

    def save_model(self, request, obj, form, change):
        """
        Allows role modification for all users, including superusers.
        Ensures the role is set to 'advisor' if left empty for superusers.
        """
        if change and obj.is_superuser and not obj.role:
            obj.role = 'advisor'
        
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)

class NewsArticleAdmin(admin.ModelAdmin):
    """
    Admin interface for managing News Articles.
    """
    list_display = ('title', 'created_at')
    search_fields = ('title',)

admin.site.register(NewsArticle, NewsArticleAdmin)

class CannedMessageCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Canned Message Categories.
    """
    list_display = ('name',)
    search_fields = ('name',)

class CannedMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Canned Messages.
    """
    list_display = ('title', 'category')
    list_filter = ('category', 'title')
    search_fields = ('title', 'content')

admin.site.register(CannedMessageCategory, CannedMessageCategoryAdmin)
admin.site.register(CannedMessage, CannedMessageAdmin)
