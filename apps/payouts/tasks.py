
import logging
from datetime import timedelta
from decimal import Decimal

import requests
from celery import shared_task
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Payout, PayoutAttempt
from .payouts import settle_payout
from .providers import ProviderRejected, get_provider
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

MPESA_LIMIT = Decimal("250000")
STATUS_QUERY_INTERVAL = timedelta(minutes=15)
STATUS_QUERY_MAX_ATTEMPTS = 5
STATUS_QUERY_AGE = timedelta(minutes=10)


def choose_method(amount):
    if amount <= MPESA_LIMIT:
        return Payout.Payment_Method.MPESA
    return Payout.Payment_Method.BANK


def _fail(payout, reason):
    payout.status = Payout.Status.FAILED
    payout.failure_reason = str(reason)[:255]
    payout.save(
        update_fields=["status", "failure_reason", "updated_at"]
    )

    PayoutAttempt.objects.filter(
        payout=payout,
        provider_ref=payout.provider_ref,
    ).update(
        status=PayoutAttempt.Status.FAILED,
        failure_reason=str(reason)[:255],
    )


def _mark_unknown(payout, reason):
    payout.status = Payout.Status.UNKNOWN
    payout.failure_reason = str(reason)[:255]
    payout.save(
        update_fields=["status", "failure_reason", "updated_at"]
    )

    PayoutAttempt.objects.filter(
        payout=payout,
        provider_ref=payout.provider_ref,
    ).update(
        status=PayoutAttempt.Status.UNKNOWN,
        failure_reason=str(reason)[:255],
    )
    
@shared_task
def send_payout(payout_id):
    with transaction.atomic():
        payout = (
            Payout.objects
            .select_for_update(of=("self",))
            .select_related("claim__insurer")
            .get(pk=payout_id)
        )

        if payout.status != Payout.Status.PENDING:
            return

        if not payout.claim.insurer_id:
            logger.error(
                "Payout %s belongs to a claim without an insurer.",
                payout.pk,
            )
            _fail(payout, "Claim has no assigned insurer.")
            return

        if not payout.claim.insurer.is_active:
            logger.error(
                "Payout %s belongs to inactive insurer %s.",
                payout.pk,
                payout.claim.insurer_id,
            )
            _fail(payout, "Insurer is inactive.")
            return

        payout.method = choose_method(payout.amount)

        try:
            provider = get_provider(payout.method)
        except ProviderRejected as exc:
            payout.save(update_fields=["method", "updated_at"])
            _fail(payout, exc)
            return
        
        payout.status = Payout.Status.PROCESSING
        payout.attempts += 1
        payout.provider_ref = provider.reference_for(payout)

        attempt = PayoutAttempt.objects.create(
            payout=payout,
            attempt_number=payout.attempts,
            provider_ref=payout.provider_ref,
            status=PayoutAttempt.Status.PROCESSING,
        )

        payout.save(
            update_fields=[
                "method",
                "status",
                "attempts",
                "provider_ref",
                "updated_at",
            ]
        )

    try:
        provider.send(payout)

    except ProviderRejected as exc:
        _fail(payout, exc)
        return

    except requests.RequestException as exc:
        logger.exception(
            "Uncertain payout outcome for payout %s", payout.pk
        )
        _mark_unknown(
            payout,
            f"Provider request outcome uncertain: {type(exc).__name__}",
        )
        return

    if provider.auto_settle:
        settle_payout(payout.provider_ref, success=True)


@shared_task
def recover_stuck_payouts():
    cutoff = timezone.now() - STATUS_QUERY_AGE

    pending_ids = Payout.objects.filter(
        status=Payout.Status.PENDING,
        created_at__lt=cutoff,
        claim__insurer__is_active=True,
    ).exclude(
        claim__insurer__isnull=True,
    ).values_list("pk", flat=True)

    for payout_id in pending_ids.iterator():
        send_payout.delay(payout_id)

    stuck = Payout.objects.filter(
        status=Payout.Status.PROCESSING,
        updated_at__lt=cutoff,
        claim__insurer__is_active=True,
    ).exclude(
        claim__insurer__isnull=True,
    )

    for payout in stuck.iterator():
        logger.warning(
            "Payout %s for insurer %s stuck in processing since %s",
            payout.pk,
            payout.claim.insurer_id,
            payout.updated_at,
        )

@shared_task
def reconcile_uncertain_payouts():

    now = timezone.now()
    cutoff = now - STATUS_QUERY_AGE
    retry_before = now - STATUS_QUERY_INTERVAL

    eligible = Payout.objects.filter(
        method=Payout.Payment_Method.MPESA,
        status__in=[
            Payout.Status.PROCESSING,
            Payout.Status.UNKNOWN,
        ],
        updated_at__lt=cutoff,
        status_query_attempts__lt=STATUS_QUERY_MAX_ATTEMPTS,
        claim__insurer__is_active=True,
    ).exclude(
        claim__insurer__isnull=True,
    ).filter(
        Q(last_status_query_at__isnull=True)
        | Q(last_status_query_at__lt=retry_before)
    )

    for payout_id in eligible.values_list("pk", flat=True).iterator():
        # Claim this attempt before making the external request.
        with transaction.atomic():
            payout = (
                Payout.objects.select_for_update()
                .filter(pk=payout_id)
                .first()
            )

            if payout is None:
                continue

            if payout.status not in (
                Payout.Status.PROCESSING,
                Payout.Status.UNKNOWN,
            ):
                continue

            if payout.method != Payout.Payment_Method.MPESA:
                continue

            if payout.status_query_attempts >= STATUS_QUERY_MAX_ATTEMPTS:
                continue

            if payout.updated_at >= cutoff:
                continue

            if (
                payout.last_status_query_at
                and payout.last_status_query_at >= retry_before
            ):
                continue

            if not payout.provider_ref:
                logger.error(
                    "Payout %s has no provider reference; "
                    "manual reconciliation required.",
                    payout.pk,
                )
                continue

            payout.status_query_attempts += 1
            payout.last_status_query_at = now
            payout.save(
                update_fields=[
                    "status_query_attempts",
                    "last_status_query_at",
                    "updated_at",
                ]
            )

            # Copy values needed after the transaction.
            payout_id_for_log = payout.pk

        try:
            provider = get_provider(Payout.Payment_Method.MPESA)
            response = provider.query_transaction_status(payout)

            query_ref = response.get("OriginatorConversationID")

            if not query_ref:
                logger.error(
                    "Status query for payout %s returned no query reference.",
                    payout_id_for_log,
                )
                continue

            # Save the reference only while the payout is still unresolved.
            updated = Payout.objects.filter(
                pk=payout_id_for_log,
                status__in=[
                    Payout.Status.PROCESSING,
                    Payout.Status.UNKNOWN,
                ],
            ).update(status_query_ref=query_ref)

            if updated:
                logger.info(
                    "Status query submitted for payout %s.",
                    payout_id_for_log,
                )

        except ProviderRejected as exc:
            logger.warning(
                "Status query submission failed for payout %s: %s",
                payout_id_for_log,
                exc,
            )

@shared_task
def send_payout_success_email(payout_id):
    try:
        payout = Payout.objects.select_related(
            "claim__user"
        ).get(pk=payout_id)
    except Payout.DoesNotExist:
        logger.error("Payout %s does not exist", payout_id)
        return

    if payout.status != Payout.Status.PAID:
        return

    recipient = payout.claim.user.email

    if not recipient:
        logger.warning(
            "No email address for payout %s",
            payout.pk,
        )
        return

    send_mail(
        subject="Your insurance payout has been completed",
        message=(
            f"Your payout of KSh {payout.amount} "
            "has been completed successfully.\n\n"
            f"Payout reference: {payout.provider_ref}\n"
            "Thank you."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )
