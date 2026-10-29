import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Payout
from .payouts import settle_payout
from .providers import ProviderRejected, get_provider

logger = logging.getLogger(__name__)

MPESA_LIMIT = Decimal("250000") 


def choose_method(amount):
    return Payout.Payment_Method.MPESA if amount <= MPESA_LIMIT else Payout.Payment_Method.BANK


def _fail(payout, reason):
    payout.status = Payout.Status.FAILED
    payout.failure_reason = str(reason)[:255]
    payout.save(update_fields=["status", "failure_reason", "updated_at"])


@shared_task
def send_payout(payout_id):
    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(pk=payout_id)
        if payout.status != Payout.Status.PENDING:
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
        payout.save(update_fields=[
            "method", "status", "attempts", "provider_ref", "updated_at",
        ])

    try:
        provider.send(payout)
    except ProviderRejected as exc:
        _fail(payout, exc)
        return

    if provider.auto_settle:
        settle_payout(payout.provider_ref, success=True)


@shared_task
def recover_stuck_payouts():
    cutoff = timezone.now() - timedelta(minutes=10)

    for p in Payout.objects.filter(status=Payout.Status.PENDING, created_at__lt=cutoff):
        send_payout.delay(p.pk)

    stuck = Payout.objects.filter(status=Payout.Status.PROCESSING, updated_at__lt=cutoff)
    for p in stuck:
        logger.warning("Payout %s stuck in processing since %s", p.pk, p.updated_at)