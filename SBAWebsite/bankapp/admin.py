from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from .models import AdvisorClientPairing

#Assigning advisors in admin.py for old clients
class AdvisorClientPairingAdmin(admin.ModelAdmin):
    """
    Advisor-Client Pairing Admin
    - Allows manual assignment of advisors to existing clients.
    - Keeps the admin interface clean and maintainable.
    """
    list_display = ['client', 'advisor']
    list_filter = ['advisor']
    search_fields = ['client__email', 'advisor__email']

admin.site.register(AdvisorClientPairing, AdvisorClientPairingAdmin)

#Updating user roles in admin.py
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin
    - Allows role editing for all users, including superusers.
    - Ensures changes are saved correctly without affecting other users.
    """
    model = User
    list_display = ['email', 'username', 'role', 'is_superuser', 'is_active']
    list_filter = ['role', 'is_superuser', 'is_active']
    ordering = ['email']
    search_fields = ['email', 'username']

    # Display the role field in the admin panel
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {
            'fields': ('role',)
        }),
    )

    # Allow role editing in the add user form as well
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {
            'fields': ('role',),
        }),
    )

    # Override save_model to allow role modification for superusers
    def save_model(self, request, obj, form, change):
        # Allow role editing for all users, including superusers
        if change and obj.is_superuser:
            # Ensure role is set to advisor if it's empty
            if not obj.role:
                obj.role = 'advisor'
        
        # Save the user with the modified role
        super().save_model(request, obj, form, change)

# Register the Custom User Admin
admin.site.register(User, CustomUserAdmin)
