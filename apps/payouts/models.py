# claims/models.py
from django.db import models
from apps.claims.models import Claim
from django.contrib.auth import get_user_model

User = get_user_model()


class BankBeneficiary(models.Model):
    class Currency(models.TextChoices):
        KES = "KES", "Kenyan Shilling"
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bank_beneficiaries",
    )

    beneficiary_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=34)
    bank_name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=20)

    branch_name = models.CharField(max_length=100, blank=True)
    branch_code = models.CharField(max_length=20, blank=True)

    swift_code = models.CharField(max_length=11, blank=True)
    country_code = models.CharField(max_length=2, default="KE")

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.KES,
    )

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.beneficiary_name} - {self.bank_name}"

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
    bank_beneficiary = models.ForeignKey(
        BankBeneficiary,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="payouts",
        )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


