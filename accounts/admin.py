from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


class UserAdmin(DjangoUserAdmin):
    """Django's UserAdmin, adapted for an email-only user with no username."""

    ordering = ['email']
    list_display = ['email', 'is_staff', 'is_active']
    search_fields = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['date_joined']


admin.site.register(User, UserAdmin)
