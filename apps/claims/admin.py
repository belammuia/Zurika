from django.contrib import admin
from .models import Claim
@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "queue", "priority", "assigned_officer", "claim_date")
    list_filter = ("queue", "status", "priority")
    search_fields = ("id", "user__email")
