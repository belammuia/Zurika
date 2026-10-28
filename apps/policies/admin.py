from django.contrib import admin
from .models import Policy


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "vehicle", "status",
        "start_date", "end_date", "coverage_limit",
    )
    list_filter = ("status",)
    search_fields = ("user__email",)