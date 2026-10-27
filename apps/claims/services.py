
from decimal import Decimal

from .models import Claim, SupportingDocument
from django.utils import timezone
from datetime import timedelta
import random
from django.db import transaction
from .routing import assign_claim, NoAvailableOfficerError
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from apps.accounts.models import OfficerProfile


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


AUDIT_SAMPLE_RATE = 0.10
MAX_RECENT_CLAIMS = 2
NEW_POLICY_DAYS = 30

def fast_track_rejection_reason(claim):
    others = (Claim.objects.filter(vehicle=claim.vehicle)
    .exclude(pk=claim.pk)
    )

    window = timedelta(days=7)

    start = claim.incident_date - window
    end = claim.incident_date + window

    if others.filter(incident_date__range=(start, end)).exists():
        return "possible duplicate"

    since = timezone.localdate() - timedelta(days=90)

    if others.filter(claim_date__gte=since).count() > MAX_RECENT_CLAIMS:
        return "frequent claimant"

    policy = claim.claim_policies.select_related("policy").first()

    if policy and (claim.incident_date - policy.policy.start_date).days < NEW_POLICY_DAYS:
        return "incident soon after policy start"

    if random.random() < AUDIT_SAMPLE_RATE:
        return "random audit sample"

    return None

@transaction.atomic
def process_fast_track(claim):
    claim = Claim.objects.select_for_update().get(pk=claim.pk)

    if claim.status != Claim.Status.SUBMITTED or claim.queue != Claim.Queue.FAST_TRACK:
        return claim 

    reason = fast_track_rejection_reason(claim)
    if reason:
        claim.queue = Claim.Queue.OFFICER
        claim.decision_reason = f"Escalated: {reason}"
        claim.save(update_fields=["queue", "decision_reason"])
    else:
        claim.status = Claim.Status.APPROVED
        claim.decision_source = "auto"
        claim.decision_reason = "Passed fast-track checks"
        claim.save(update_fields=["status", "decision_source", "decision_reason"])
    return claim

def process_claim(claim):
    triage_claim(claim)
    claim.refresh_from_db()

    if claim.queue == Claim.Queue.FAST_TRACK:
        claim = process_fast_track(claim)

    if claim.queue in (Claim.Queue.OFFICER, Claim.Queue.SENIOR) \
            and claim.status != Claim.Status.APPROVED:
        try:
            assign_claim(claim)
        except NoAvailableOfficerError:
            pass
    return claim

@transaction.atomic
def review_claim(claim, officer, decision, reason):
    claim = Claim.objects.select_for_update().get(pk=claim.pk)

    if claim.assigned_officer_id != officer.id:
        raise PermissionDenied("This claim is not assigned to you")

    if claim.status != Claim.Status.SUBMITTED:
        raise ValidationError("This claim either has insuffient documents or the decision has been made")

    claim.status = decision
    claim.decision_source = 'officer'
    claim.decision_reason = reason

    claim.save(update_fields=["status","decision_source", "decision_reason"])

    profile = OfficerProfile.objects.select_for_update().get(officer=officer)
    profile.availability = OfficerProfile.Availability.AVAILABLE
    profile.save(update_fields=["availability"])

    return claim





