from django.db import transaction
from ..models import Claim, Payout,PayoutAttempt


@transaction.atomic
def create_payout(claim):
    from ..tasks import send_payout

    if not claim.insurer_id:
        raise ValueError("Claim must belong to an insurer.")

    if not claim.insurer.is_active:
        raise ValueError("Cannot pay claims for an inactive insurer.")

    if claim.status != Claim.Status.APPROVED:
        raise ValueError("Only approved claims can be paid.")

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
        transaction.on_commit(
            lambda: send_payout.delay(payout.pk)
        )

    return payout

@transaction.atomic
def settle_payout(provider_ref, success, reason=""):
    """Called by the provider callback, or by the fake provider."""

    payout = (
        Payout.objects
        .select_for_update()
        .get(provider_ref=provider_ref)
    )

    attempt = (
        PayoutAttempt.objects
        .select_for_update()
        .filter(
            payout=payout,
            provider_ref=provider_ref,
        )
        .first()
    )

    if payout.status in (Payout.Status.PAID, Payout.Status.FAILED):
        return payout

    payout.status = (
        Payout.Status.PAID if success else Payout.Status.FAILED
    )
    payout.failure_reason = "" if success else str(reason)[:255]

    payout.save(
        update_fields=["status", "failure_reason", "updated_at"]
    )

    if attempt:
        attempt.status = (
            PayoutAttempt.Status.SUCCESS
            if success
            else PayoutAttempt.Status.FAILED
        )
        attempt.failure_reason = "" if success else str(reason)[:255]
        attempt.save(
            update_fields=["status", "failure_reason", "updated_at"]
        )

    if success:
        from ..tasks import send_payout_success_email

        transaction.on_commit(
            lambda: send_payout_success_email.delay(payout.pk)
        )

    return payout


@transaction.atomic
def retry_failed_payout(payout_id):
    payout = (
        Payout.objects
        .select_for_update(of=("self",))
        .select_related("claim__insurer")
        .get(pk=payout_id)
        )

    if payout.status != Payout.Status.FAILED:
        raise ValueError("ONly claims that have failed can be retried")
    
    if payout.claim.status != Claim.Status.APPROVED:
        raise ValueError("The claim is no longer approved.")

    if not payout.claim.insurer_id or not payout.claim.insurer.is_active:
        raise ValueError("The insurer is missing or inactive.")

    prev_attempt = (
        payout
        .payment_attempts
        .order_by("-attempt_number")
        .first()
        )
    if not prev_attempt:
        raise ValueError("No previous attempts exist")

    if prev_attempt.status != PayoutAttempt.Status.FAILED:
        raise ValueError("The previous attempt is not confirmed as failed.")

    payout.status = Payout.Status.PENDING
    payout.failure_reason = ""

    payout.save(
        update_fields=["status", "failure_reason", "updated_at"]
    )

    from ..tasks import send_payout

    transaction.on_commit(
        lambda: send_payout.delay(payout.pk)
    )

    return payout