
from decimal import Decimal

from .models import Claim, SupportingDocument


FAST_TRACK_THRESHOLD = Decimal("50000.00")
STANDARD_CLAIM_THRESHOLD_MAX = Decimal("250000.00")



def triage_claim(claim):
    if claim.has_injury or claim.severe_structural_damage:
        severity = Claim.Severity.CRITICAL
        priority = Claim.Priority.URGENT

    elif claim.third_party_involved:
        severity = Claim.Severity.HIGH
        priority = Claim.Priority.HIGH

    elif claim.estimated_cost > STANDARD_CLAIM_THRESHOLD_MAX:
        severity = Claim.Severity.HIGH
        priority = Claim.Priority.HIGH

    elif claim.vehicles_involved >= 2:
        severity = Claim.Severity.MEDIUM
        priority = Claim.Priority.NORMAL

    elif claim.estimated_cost >= FAST_TRACK_THRESHOLD:
        severity = Claim.Severity.MEDIUM
        priority = Claim.Priority.NORMAL

    else:
        severity = Claim.Severity.MINOR
        priority = Claim.Priority.LOW

    if claim.multi_policy_flag:
        queue = Claim.Queue.AUDIT

    elif claim.has_injury or claim.severe_structural_damage:
        queue = Claim.Queue.SENIOR

    elif claim.third_party_involved:
        queue = Claim.Queue.SENIOR

    elif claim.estimated_cost > STANDARD_CLAIM_THRESHOLD_MAX:
        queue = Claim.Queue.SENIOR

    elif claim.vehicles_involved >= 2:
        queue = Claim.Queue.OFFICER

    elif claim.estimated_cost >= FAST_TRACK_THRESHOLD:
        queue = Claim.Queue.OFFICER

    else:
        queue = Claim.Queue.FAST_TRACK

    claim.severity = severity
    claim.priority = priority
    claim.queue = queue

    claim.save(update_fields=["severity", "priority", "queue"])

    return claim


def has_required_documents(claim):
    required_document_types = {"accident_photos"}

    uploaded_document_types = set(
        claim.documents.values_list("document_type", flat=True)
    )

    return required_document_types.issubset(uploaded_document_types)



