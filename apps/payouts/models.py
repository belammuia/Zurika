# claims/models.py
from django.db import models
from apps.claims.models import Claim


class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PAID = "paid", "Paid"
        UNKNOWN = "unknown", "Unknown - Reconciliation Required"
        FAILED = "failed", "Failed"

    class Payment_Method(models.TextChoices):
        MPESA = "mpesa", "M-Pesa"
        BANK = "bank", "Bank"

    claim = models.OneToOneField(Claim, on_delete=models.PROTECT, related_name="payout")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=Payment_Method.choices, default=Payment_Method.MPESA)
    destination = models.CharField(max_length=20)  
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    provider_ref = models.CharField(max_length=100, blank=True, db_index=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    status_query_ref = models.CharField(max_length=100,blank=True,db_index=True)
    status_query_attempts = models.PositiveSmallIntegerField(default=0)
    last_status_query_at = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)