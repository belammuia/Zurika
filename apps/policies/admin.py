
from django.contrib import admin
from .models import Vehicle, VehicleImage, Policy


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "owner",
        "name",
        "registration_number",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "owner__email",
        "name",
        "registration_number",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "created_at")
    search_fields = ("vehicle__registration_number",)


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "vehicle",
        "insurer",
        "policy_type",
        "status",
        "start_date",
        "end_date",
        "coverage_limit",
    )
    list_filter = ("status", "policy_type", "insurer")
    search_fields = (
        "user__email",
        "vehicle__registration_number",
        "policy_number",
        "insurer__name",
    )
    readonly_fields = ("created_at", "updated_at")
