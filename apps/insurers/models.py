from django.conf import settings
from django.db import models


class Insurer(models.Model):
    name = models.CharField(max_length=150, unique=True)
    legal_name = models.CharField(max_length=200, blank=True)
    registration_number = models.CharField(
        max_length=100,
        blank=True,
    )
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InsurerMembership(models.Model):

    class Role(models.TextChoices):
        ADMIN = "admin", "Insurer Administrator"
        OFFICER = "claims_officer", "Claims Officer"
        SENIOR_OFFICER = "senior_officer", "Senior Claims Officer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="insurer_memberships",
    )

    insurer = models.ForeignKey(
        Insurer,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "insurer"],
                name="unique_user_insurer_membership",
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.insurer.name} ({self.role})"