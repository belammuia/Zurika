
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Claim
from apps.accounts.models import OfficerProfile

User = get_user_model()


class NoAvailableOfficerError(Exception):
    pass


def get_required_role(claim):
    # PSEUDOCODE:
    # 1. Check the claim's queue.
    # 2. Map the queue to the appropriate officer role.
    # 3. Raise an error if the queue has no configured role.

    if claim.queue == Claim.Queue.OFFICER:
        return User.Role.OFFICER

    if claim.queue == Claim.Queue.SENIOR:
        return User.Role.SENIOR_OFFICER

    raise ValueError(
        f"No automatic officer role configured for queue: {claim.queue}"
    )


@transaction.atomic
def assign_claim(claim):
    # PSEUDOCODE:
    # 1. Start a database transaction.
    # 2. Lock the claim row.
    # 3. Determine the required role from the locked claim.
    # 4. Stop if the claim is already assigned.
    # 5. Find and lock an available, active officer
    #    whose role matches the required role.
    # 6. Raise an exception if no eligible officer exists.
    # 7. Assign the officer to the claim.
    # 8. Mark the officer as busy.
    # 9. Save both changes within the transaction.
    # 10. Return the updated claim.

    locked_claim = Claim.objects.select_for_update().get(
        pk=claim.pk
    )

    required_role = get_required_role(locked_claim)

    if locked_claim.assigned_officer_id is not None:
        raise ValueError("Claim is already assigned.")

    available_officer_profile = (
        OfficerProfile.objects
        .select_for_update()
        .filter(
            availability=OfficerProfile.Availability.AVAILABLE,
            officer__role=required_role,
            officer__is_active=True,
        )
        .order_by("pk")
        .first()
    )

    if available_officer_profile is None:
        raise NoAvailableOfficerError(
            "No eligible officers are available."
        )

    assigned_officer = available_officer_profile.officer

    locked_claim.assigned_officer = assigned_officer
    locked_claim.save(update_fields=["assigned_officer"])

    available_officer_profile.availability = (
        OfficerProfile.Availability.BUSY
    )
    available_officer_profile.save(update_fields=["availability"])

    return locked_claim
