from django.conf import settings
from django.db import models
from auditlog.registry import auditlog


class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles")
    name = models.CharField(max_length=100)  
    registration_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.registration_number

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Policy(models.Model):
    class PolicyType(models.TextChoices):
        THIRD_PARTY = "third_party", "Third Party Only"
        TPFT = "tpft", "Third Party, Fire & Theft"
        COMPREHENSIVE = "comprehensive", "Comprehensive"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="policies")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="policies")
    policy_number = models.CharField(max_length=50, unique=True)
    policy_type = models.CharField(max_length=20, choices=PolicyType.choices, default=PolicyType.THIRD_PARTY)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    coverage_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    insurer = models.ForeignKey(
        "insurers.Insurer",
        on_delete=models.PROTECT,
        related_name="policies",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.policy_number

auditlog.register(
    Vehicle,
    include_fields=[
        "owner",
        "name",
        "registration_number",
        "created_at",
        "updated_at",
    ],
)

auditlog.register(
    Policy,
    include_fields=[
        "user",
        "vehicle",
        "policy_number",
        "policy_type",
        "status",
        "start_date",
        "end_date",
        "insurer_name",
        "created_at",
        "updated_at",
    ],
)