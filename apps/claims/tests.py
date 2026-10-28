
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase

from .models import Claim
from .services import triage_claim


class ClaimTriageTests(SimpleTestCase):
    def make_claim(self, **overrides):
        defaults = {
            "estimated_cost": Decimal("30000.00"),
            "has_injury": False,
            "severe_structural_damage": False,
            "multi_policy_flag": False,
            "third_party_involved": False,
            "vehicles_involved": 1,
            "severity": "",
            "priority": "",
            "queue": "",
            "save": Mock(),
        }

        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_claim_below_50000_goes_to_fast_track(self):
        claim = self.make_claim(
            estimated_cost=Decimal("49999.99")
        )

        triage_claim(claim)

        self.assertEqual(claim.queue, Claim.Queue.FAST_TRACK)
        self.assertEqual(claim.severity, Claim.Severity.MINOR)
        self.assertEqual(claim.priority, Claim.Priority.LOW)

    def test_claim_at_50000_goes_to_officer(self):
        claim = self.make_claim(
            estimated_cost=Decimal("50000.00")
        )

        triage_claim(claim)

        self.assertEqual(claim.queue, Claim.Queue.OFFICER)
        self.assertEqual(claim.severity, Claim.Severity.MEDIUM)

    def test_claim_at_250000_goes_to_officer(self):
        claim = self.make_claim(
            estimated_cost=Decimal("250000.00")
        )

        triage_claim(claim)

        self.assertEqual(claim.queue, Claim.Queue.OFFICER)

    def test_claim_above_250000_goes_to_senior(self):
        claim = self.make_claim(
            estimated_cost=Decimal("250000.01")
        )

        triage_claim(claim)

        self.assertEqual(claim.queue, Claim.Queue.SENIOR)
        self.assertEqual(claim.severity, Claim.Severity.HIGH)

    def test_injury_requires_critical_senior_review(self):
        claim = self.make_claim(has_injury=True)

        triage_claim(claim)

        self.assertEqual(claim.severity, Claim.Severity.CRITICAL)
        self.assertEqual(claim.priority, Claim.Priority.URGENT)
        self.assertEqual(claim.queue, Claim.Queue.SENIOR)

    def test_third_party_claim_goes_to_senior(self):
        claim = self.make_claim(third_party_involved=True)

        triage_claim(claim)

        self.assertEqual(claim.severity, Claim.Severity.HIGH)
        self.assertEqual(claim.queue, Claim.Queue.SENIOR)

    def test_multiple_vehicles_cannot_fast_track(self):
        claim = self.make_claim(vehicles_involved=2)

        triage_claim(claim)

        self.assertEqual(claim.queue, Claim.Queue.OFFICER)

    def test_multi_policy_claim_goes_to_audit(self):
        claim = self.make_claim(multi_policy_flag=True)

        triage_claim(claim)

        self.assertEqual(claim.queue, Claim.Queue.AUDIT)

    def test_severe_structural_damage_is_critical(self):
        claim = self.make_claim(severe_structural_damage=True)

        triage_claim(claim)

        self.assertEqual(claim.severity, Claim.Severity.CRITICAL)
        self.assertEqual(claim.queue, Claim.Queue.SENIOR)


    def test_low_cost_claim_with_injury_goes_to_senior(self):
        claim = self.make_claim(
            estimated_cost=Decimal("20000.00"),
            has_injury=True,
        )

        triage_claim(claim)

        self.assertEqual(claim.severity, Claim.Severity.CRITICAL)
        self.assertEqual(claim.priority, Claim.Priority.URGENT)
        self.assertEqual(claim.queue, Claim.Queue.SENIOR)

    def test_low_cost_third_party_claim_goes_to_senior(self):
        claim = self.make_claim(
            estimated_cost=Decimal("20000.00"),
            third_party_involved=True,
        )

        triage_claim(claim)

        self.assertEqual(claim.severity, Claim.Severity.HIGH)
        self.assertEqual(claim.queue, Claim.Queue.SENIOR)

    def test_multi_policy_claim_with_injury_keeps_critical_severity(self):
        claim = self.make_claim(
            estimated_cost=Decimal("20000.00"),
            has_injury=True,
            multi_policy_flag=True,
        )

        triage_claim(claim)

        self.assertEqual(claim.severity, Claim.Severity.CRITICAL)
        self.assertEqual(claim.queue, Claim.Queue.AUDIT)

    def test_triage_saves_only_triage_fields(self):
        claim = self.make_claim()

        triage_claim(claim)

        claim.save.assert_called_once_with(
            update_fields=["severity", "priority", "queue"]
        )

    def test_triage_does_not_approve_claim(self):
        claim = self.make_claim()
        claim.status = Claim.Status.SUBMITTED

        triage_claim(claim)

        self.assertEqual(claim.status, Claim.Status.SUBMITTED)


