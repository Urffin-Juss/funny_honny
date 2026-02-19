from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CRMUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CRM", {"fields": ("role",)}),)
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
