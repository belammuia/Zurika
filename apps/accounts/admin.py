
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auditlog.models import LogEntry
from auditlog.admin import LogEntryAdmin as BaseLogEntryAdmin

from .models import User, Profile, OfficerProfile


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "role",
        "is_staff",
        "is_active",
        "created_at",
    )

    list_filter = (
        "role",
        "is_staff",
        "is_active",
    )

    search_fields = ("email",)
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Role and access", {
            "fields": (
                "role",
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {
            "fields": ("last_login", "created_at", "updated_at")
        }),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "role",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "user",
        "updated_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "user__email",
    )

    readonly_fields = ("updated_at",)

@admin.register(OfficerProfile)
class OfficerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "officer",
        "availability",
    )



admin.site.unregister(LogEntry)
admin.site.register(LogEntry, BaseLogEntryAdmin)
