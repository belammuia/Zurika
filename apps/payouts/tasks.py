from celery import shared_task
from .models import Payout
from .payouts import settle_payout
from .providers import get_provider, ProviderRejected
from django.db import transaction
import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_payout(payout_id):
    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(pk=payout_id)
        if payout.status != Payout.Status.PENDING:
            return  
        payout.status = Payout.Status.PROCESSING
        payout.attempts += 1
        payout.save(update_fields=["status", "attempts", "updated_at"])

    provider = get_provider(payout.method)
    try:
        ref = provider.send(payout)
    except ProviderRejected as exc:
        payout.status = Payout.Status.FAILED
        payout.failure_reason = str(exc)[:255]
        payout.save(update_fields=["status", "failure_reason", "updated_at"])
        return

    payout.provider_ref = ref
    payout.save(update_fields=["provider_ref", "updated_at"])

    if provider.auto_settle:
        settle_payout(ref, success=True)



@shared_task
def recover_stuck_payouts():
    cutoff = timezone.now() - timedelta(minutes=10)

    for p in Payout.objects.filter(status=Payout.Status.PENDING, created_at__lt=cutoff):
        send_payout.delay(p.pk)  # safe: send_payout only acts on pending

    stuck = Payout.objects.filter(status=Payout.Status.PROCESSING, updated_at__lt=cutoff)
    for p in stuck:
        logger.warning("Payout %s stuck in processing since %s", p.pk, p.updated_at)