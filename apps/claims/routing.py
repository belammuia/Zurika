
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Claim
from apps.accounts.models import OfficerProfile

User = get_user_model()


class NoAvailableOfficerError(Exception):
    pass


def get_required_role(claim):
    if claim.queue == Claim.Queue.OFFICER:
        return "claims_officer"

    if claim.queue == Claim.Queue.SENIOR:
        return "senior_officer"

    raise ValueError(
        f"No automatic officer role configured for queue: {claim.queue}"
    )


@transaction.atomic
def assign_claim(claim):
    locked_claim = (
        Claim.objects
        .select_for_update(of=("self",))
        .select_related("insurer")
        .get(pk=claim.pk)
    )

    if locked_claim.assigned_officer_id is not None:
        raise ValueError("Claim is already assigned.")

    if not locked_claim.insurer_id:
        raise NoAvailableOfficerError(
            "Cannot assign a claim without an insurer."
        )

    if not locked_claim.insurer.is_active:
        raise NoAvailableOfficerError(
            "Cannot assign claims belonging to an inactive insurer."
        )

    required_role = get_required_role(locked_claim)

    available_officer_profile = (
        OfficerProfile.objects
        .select_for_update()
        .filter(
            availability=OfficerProfile.Availability.AVAILABLE,
            officer__is_active=True,
            officer__insurer_memberships__insurer_id=locked_claim.insurer_id,
            officer__insurer_memberships__role=required_role,
            officer__insurer_memberships__is_active=True,
            officer__insurer_memberships__insurer__is_active=True,
        )
        .order_by("pk")
        .first()
    )

    if available_officer_profile is None:
        raise NoAvailableOfficerError(
            "No eligible officers are available for this insurer."
        )

    assigned_officer = available_officer_profile.officer

    locked_claim.assigned_officer = assigned_officer
    locked_claim.save(update_fields=["assigned_officer"])

    available_officer_profile.availability = (
        OfficerProfile.Availability.BUSY
    )
    available_officer_profile.save(update_fields=["availability"])

    return locked_claim
