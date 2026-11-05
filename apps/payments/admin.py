from django.contrib import admin
from .models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("id", "claim", "method", "status", "amount", "provider_ref", "attempts", "updated_at")
    list_filter = ("status", "method")
    search_fields = ("provider_ref", "claim__id")
    readonly_fields = ("provider_ref", "attempts", "failure_reason", "created_at", "updated_at")