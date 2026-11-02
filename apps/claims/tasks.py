
from celery import shared_task
from django.db.models import Case, IntegerField, Value, When

from .models import Claim
from .routing import assign_claim, NoAvailableOfficerError


@shared_task
def assign_pending_claims():
    priority_rank = Case(
        When(priority=Claim.Priority.URGENT, then=Value(0)),
        When(priority=Claim.Priority.HIGH, then=Value(1)),
        When(priority=Claim.Priority.NORMAL, then=Value(2)),
        default=Value(3),
        output_field=IntegerField(),
    )

    pending = (
        Claim.objects.filter(
            assigned_officer__isnull=True,
            status=Claim.Status.SUBMITTED,
            queue__in=[
                Claim.Queue.OFFICER,
                Claim.Queue.SENIOR,
            ],
            insurer__isnull=False,
            insurer__is_active=True,
        )
        .select_related("insurer")
        .annotate(rank=priority_rank)
        .order_by("rank", "claim_date", "id")
    )

    exhausted_queues = set()
    assigned = 0

    for claim in pending:
        queue_key = (claim.insurer_id, claim.queue)

        if queue_key in exhausted_queues:
            continue

        try:
            assign_claim(claim)
            assigned += 1

        except NoAvailableOfficerError:
            exhausted_queues.add(queue_key)

        except ValueError:
            continue

    return f"Assigned {assigned} pending claims."
