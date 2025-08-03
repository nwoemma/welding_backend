# api/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Import your custom User model

# Custom User Admin configuration
class CustomUserAdmin(UserAdmin):
    # Fields to display in list view
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'role')
    
    # Fields to filter by
    list_filter = ('is_staff', 'is_superuser', 'role', 'status')
    
    # Fieldsets for edit page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'address', 'sex', 'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('role', 'status', 'preferred_language')}),
    )
    
    # Fields when adding new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Register your models here
admin.site.register(User, CustomUserAdmin)

# If you have other models like Job, Notification:
# from .models import Job, Notification
# admin.site.register(Job)
# admin.site.register(Notification)