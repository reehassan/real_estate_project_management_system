# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # ── List View ──
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter   = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    # ── Detail View ──
    # Extends Django's default UserAdmin fieldsets, adds your custom 'role' field
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Permissions', {
            'fields': ('role',)
        }),
    )

    # ── Add User Form (when creating a new user) ──
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {
            'fields': ('role',)
        }),
    )

    readonly_fields = ('date_joined', 'last_login')