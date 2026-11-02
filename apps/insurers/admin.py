from django.contrib import admin

from .models import Insurer, InsurerMembership


@admin.register(Insurer)
class InsurerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "legal_name",
        "registration_number",
        "email",
        "phone_number",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active", "created_at")

    search_fields = (
        "name",
        "legal_name",
        "registration_number",
        "email",
    )

    readonly_fields = ("created_at", "updated_at")

    ordering = ("name",)


@admin.register(InsurerMembership)
class InsurerMembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "insurer",
        "role",
        "is_active",
        "created_at",
    )

    list_filter = (
        "role",
        "is_active",
        "insurer",
    )

    search_fields = (
        "user__email",
        "insurer__name",
    )

    readonly_fields = ("created_at",)

    autocomplete_fields = ("user", "insurer")

    ordering = ("insurer", "role")