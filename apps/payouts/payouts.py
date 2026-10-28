from django.db import transaction
from .models import Claim, Payout


@transaction.atomic
def create_payout(claim):
    """Idempotent: one payout per claim, and it is sent only after commit."""
    from .tasks import send_payout  
    if not claim.approved_amount or claim.approved_amount <= 0:
        raise ValueError("Nothing to pay out.")

    payout, created = Payout.objects.get_or_create(
        claim=claim,
        defaults={
            "amount": claim.approved_amount,
            "destination": claim.user.profile.phone_number,
        },
    )
    if created:
        transaction.on_commit(lambda: send_payout.delay(payout.pk))
    return payout


@transaction.atomic
def settle_payout(provider_ref, success, reason=""):
    """Called by the provider callback, or by the fake provider."""
    payout = Payout.objects.select_for_update().get(provider_ref=provider_ref)

    if payout.status in (Payout.Status.PAID, Payout.Status.FAILED):
        return payout  

    payout.status = Payout.Status.PAID if success else Payout.Status.FAILED
    payout.failure_reason = "" if success else reason[:255]
    payout.save(update_fields=["status", "failure_reason", "updated_at"])
    return payout