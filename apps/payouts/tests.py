# apps/payouts/tests.py
from decimal import Decimal
from unittest.mock import MagicMock, patch
from model_bakery import baker

import requests
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.payouts.models import Payout
from apps.claims.models import Claim
from apps.payouts.payouts import settle_payout
from apps.payouts.providers import (
    FakeProvider,
    MpesaProvider,
    ProviderRejected,
    get_provider,
    normalize_phone,
)
from apps.payouts.tasks import recover_stuck_payouts, send_payout

SECRET = "test-secret-123"

MPESA_SETTINGS = dict(
    PAYOUT_PROVIDER="mpesa",
    MPESA_ENV="sandbox",
    MPESA_CONSUMER_KEY="key",
    MPESA_CONSUMER_SECRET="secret",
    MPESA_SHORTCODE="600000",
    MPESA_INITIATOR_NAME="tester",
    MPESA_SECURITY_CREDENTIAL="cred",
    MPESA_CALLBACK_BASE_URL="https://example.ngrok-free.dev",
    MPESA_CALLBACK_SECRET=SECRET,
)


# ---------- helpers ----------

_counter = 0


def make_claim():
    # baker creates the user, vehicle and any other required relations itself
    return baker.make(
        "claims.Claim",
        status=Claim.Status.APPROVED,
        estimated_cost=Decimal("250.00"),
    )


def make_payout(status="pending", amount="250.00", ref="", phone="0712345678"):
    return Payout.objects.create(
        claim=make_claim(),
        amount=Decimal(amount),
        destination=phone,
        status=status,
        provider_ref=ref,
    )


def fake_response(status=200, body=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = body or {}
    r.text = str(body)
    if status >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(f"{status}")
    return r


# ---------- phone normalisation ----------

class NormalizePhoneTests(TestCase):
    def test_local_format(self):
        self.assertEqual(normalize_phone("0712345678"), "254712345678")

    def test_plus_international(self):
        self.assertEqual(normalize_phone("+254712345678"), "254712345678")

    def test_already_normalised(self):
        self.assertEqual(normalize_phone("254712345678"), "254712345678")

    def test_spaces_and_dashes_are_stripped(self):
        self.assertEqual(normalize_phone("0712-345 678"), "254712345678")

    def test_too_short_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            normalize_phone("12345")

    def test_wrong_country_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            normalize_phone("256712345678")


# ---------- provider selection ----------

class GetProviderTests(TestCase):
    @override_settings(PAYOUT_PROVIDER="fake")
    def test_fake_setting_always_gives_fake(self):
        self.assertIsInstance(get_provider("mpesa"), FakeProvider)

    @override_settings(PAYOUT_PROVIDER="mpesa")
    def test_mpesa_gives_mpesa(self):
        self.assertIsInstance(get_provider("mpesa"), MpesaProvider)

    @override_settings(PAYOUT_PROVIDER="mpesa")
    def test_unconfigured_method_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            get_provider("bank")


# ---------- MpesaProvider ----------

@override_settings(**MPESA_SETTINGS)
class MpesaProviderTests(TestCase):
    def send(self, response=None, side_effect=None):
        payout = make_payout(status="processing", ref="claims-1-abc")
        with patch.object(MpesaProvider, "_get_access_token", return_value="tok"), \
             patch("apps.payouts.providers.requests.post",
                   return_value=response, side_effect=side_effect) as post:
            MpesaProvider().send(payout)
        return payout, post

    def test_references_are_unique_and_carry_no_personal_data(self):
        payout = make_payout()
        provider = MpesaProvider()
        a, b = provider.reference_for(payout), provider.reference_for(payout)
        self.assertNotEqual(a, b)
        self.assertTrue(a.startswith(f"claims-{payout.pk}-"))

    def test_accepted_request_has_correct_payload(self):
        payout, post = self.send(fake_response(200, {"ResponseCode": "0"}))
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["OriginatorConversationID"], "claims-1-abc")
        self.assertEqual(payload["PartyB"], "254712345678")
        self.assertEqual(payload["Amount"], 250)
        self.assertEqual(payload["CommandID"], "BusinessPayment")
        self.assertEqual(payload["PartyA"], "600000")
        self.assertIn(SECRET, payload["ResultURL"])
        self.assertIn(SECRET, payload["QueueTimeOutURL"])
        self.assertTrue(payload["ResultURL"].startswith("https://example.ngrok-free.dev/"))

    def test_uses_sandbox_url_and_v3_endpoint(self):
        _, post = self.send(fake_response(200, {"ResponseCode": "0"}))
        self.assertEqual(
            post.call_args.args[0],
            "https://sandbox.safaricom.co.ke/mpesa/b2c/v3/paymentrequest",
        )

    @override_settings(MPESA_ENV="production")
    def test_production_env_uses_production_url(self):
        _, post = self.send(fake_response(200, {"ResponseCode": "0"}))
        self.assertTrue(post.call_args.args[0].startswith("https://api.safaricom.co.ke/"))

    def test_nonzero_response_code_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            self.send(fake_response(200, {"ResponseCode": "1", "ResponseDescription": "No"}))

    def test_4xx_is_a_definite_rejection(self):
        with self.assertRaises(ProviderRejected):
            self.send(fake_response(400, {"errorMessage": "bad request"}))

    def test_5xx_is_uncertain_and_not_swallowed(self):
        with self.assertRaises(requests.HTTPError):
            self.send(fake_response(503))

    def test_timeout_is_uncertain_and_not_swallowed(self):
        with self.assertRaises(requests.Timeout):
            self.send(side_effect=requests.Timeout())

    def test_invalid_phone_is_rejected_before_any_request(self):
        payout = make_payout(status="processing", ref="r1", phone="123")
        with patch.object(MpesaProvider, "_get_access_token", return_value="tok"), \
             patch("apps.payouts.providers.requests.post") as post:
            with self.assertRaises(ProviderRejected):
                MpesaProvider().send(payout)
        post.assert_not_called()

    def test_auth_failure_is_a_definite_rejection(self):
        with patch("apps.payouts.providers.requests.get",
                   side_effect=requests.ConnectionError()):
            with self.assertRaises(ProviderRejected):
                MpesaProvider()._get_access_token()


# ---------- send_payout task ----------

@override_settings(**MPESA_SETTINGS)
class SendPayoutTaskTests(TestCase):
    def mock_provider(self, auto_settle=False, send_side_effect=None):
        provider = MagicMock()
        provider.auto_settle = auto_settle
        provider.reference_for.return_value = "ref-1"
        provider.send.side_effect = send_side_effect
        return provider

    def test_accepted_send_leaves_payout_processing(self):
        payout = make_payout()
        provider = self.mock_provider()
        with patch("apps.payouts.tasks.get_provider", return_value=provider):
            send_payout(payout.pk)
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PROCESSING)
        self.assertEqual(payout.provider_ref, "ref-1")
        self.assertEqual(payout.attempts, 1)
        provider.send.assert_called_once()

    def test_reference_is_saved_before_the_send(self):
        payout = make_payout()
        seen = {}

        def check(p):
            seen["ref"] = Payout.objects.get(pk=p.pk).provider_ref

        provider = self.mock_provider(send_side_effect=check)
        with patch("apps.payouts.tasks.get_provider", return_value=provider):
            send_payout(payout.pk)
        self.assertEqual(seen["ref"], "ref-1")

    def test_definite_rejection_marks_failed(self):
        payout = make_payout()
        provider = self.mock_provider(send_side_effect=ProviderRejected("invalid number"))
        with patch("apps.payouts.tasks.get_provider", return_value=provider):
            send_payout(payout.pk)
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.FAILED)
        self.assertEqual(payout.failure_reason, "invalid number")

    def test_uncertain_failure_leaves_processing(self):
        payout = make_payout()
        provider = self.mock_provider(send_side_effect=requests.Timeout())
        with patch("apps.payouts.tasks.get_provider", return_value=provider):
            with self.assertRaises(requests.Timeout):
                send_payout(payout.pk)
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PROCESSING)

    def test_running_the_task_twice_sends_once(self):
        payout = make_payout()
        provider = self.mock_provider()
        with patch("apps.payouts.tasks.get_provider", return_value=provider):
            send_payout(payout.pk)
            send_payout(payout.pk)
        self.assertEqual(provider.send.call_count, 1)
        payout.refresh_from_db()
        self.assertEqual(payout.attempts, 1)

    def test_uncertain_payout_is_not_resent_by_a_retry(self):
        payout = make_payout()
        provider = self.mock_provider(send_side_effect=requests.Timeout())
        with patch("apps.payouts.tasks.get_provider", return_value=provider):
            with self.assertRaises(requests.Timeout):
                send_payout(payout.pk)
            send_payout(payout.pk)  # must do nothing
        self.assertEqual(provider.send.call_count, 1)

    def test_auto_settle_provider_ends_paid(self):
        payout = make_payout()
        provider = self.mock_provider(auto_settle=True)
        with patch("apps.payouts.tasks.get_provider", return_value=provider):
            send_payout(payout.pk)
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PAID)

    def test_large_amount_without_bank_provider_fails_cleanly(self):
        payout = make_payout(amount="300000.00")
        send_payout(payout.pk)  # real get_provider: no "bank" provider yet
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.FAILED)
        self.assertIn("bank", payout.failure_reason.lower())


# ---------- recovery task ----------

class RecoverStuckPayoutsTests(TestCase):
    def age(self, payout, minutes):
        from datetime import timedelta
        from django.utils import timezone
        past = timezone.now() - timedelta(minutes=minutes)
        Payout.objects.filter(pk=payout.pk).update(created_at=past, updated_at=past)

    def test_old_pending_payout_is_requeued(self):
        payout = make_payout(status="pending")
        self.age(payout, 30)
        with patch("apps.payouts.tasks.send_payout.delay") as delay:
            recover_stuck_payouts()
        delay.assert_called_once_with(payout.pk)

    def test_fresh_pending_payout_is_left_alone(self):
        make_payout(status="pending")
        with patch("apps.payouts.tasks.send_payout.delay") as delay:
            recover_stuck_payouts()
        delay.assert_not_called()

    def test_stuck_processing_payout_is_never_resent(self):
        payout = make_payout(status="processing", ref="r1")
        self.age(payout, 30)
        with patch("apps.payouts.tasks.send_payout.delay") as delay:
            recover_stuck_payouts()
        delay.assert_not_called()


# ---------- settle_payout ----------

class SettlePayoutTests(TestCase):
    def test_success_marks_paid(self):
        payout = make_payout(status="processing", ref="r1")
        settle_payout("r1", success=True)
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PAID)

    def test_failure_records_reason(self):
        payout = make_payout(status="processing", ref="r1")
        settle_payout("r1", success=False, reason="Insufficient funds")
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.FAILED)
        self.assertEqual(payout.failure_reason, "Insufficient funds")

    def test_second_settle_changes_nothing(self):
        payout = make_payout(status="processing", ref="r1")
        settle_payout("r1", success=True)
        settle_payout("r1", success=False, reason="late duplicate")
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PAID)


# ---------- M-Pesa callbacks ----------

@override_settings(MPESA_CALLBACK_SECRET=SECRET)
class MpesaCallbackTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.payout = make_payout(status="processing", ref="claims-1-abc")
        self.result_url = f"/api/v1/payouts/mpesa/result/{SECRET}/"
        self.timeout_url = f"/api/v1/payouts/mpesa/timeout/{SECRET}/"

    def body(self, code, ref="claims-1-abc"):
        return {"Result": {"ResultCode": code, "ResultDesc": "x",
                           "OriginatorConversationID": ref}}

    def test_success_marks_paid(self):
        res = self.api.post(self.result_url, self.body(0), format="json")
        self.assertEqual(res.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_failure_code_marks_failed(self):
        self.api.post(self.result_url, self.body(2001), format="json")
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.FAILED)

    def test_result_code_as_string_is_handled(self):
        self.api.post(self.result_url, self.body("0"), format="json")
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_duplicate_callback_is_ignored(self):
        self.api.post(self.result_url, self.body(0), format="json")
        self.api.post(self.result_url, self.body(2001), format="json")
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_wrong_secret_is_404_and_changes_nothing(self):
        res = self.api.post("/api/v1/payouts/mpesa/result/wrong/", self.body(0), format="json")
        self.assertEqual(res.status_code, 404)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PROCESSING)

    def test_unknown_reference_is_acknowledged_without_error(self):
        res = self.api.post(self.result_url, self.body(0, ref="nope"), format="json")
        self.assertEqual(res.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PROCESSING)

    def test_timeout_callback_leaves_payout_processing(self):
        res = self.api.post(self.timeout_url, {"Result": {}}, format="json")
        self.assertEqual(res.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PROCESSING)

    def test_timeout_with_wrong_secret_is_404(self):
        res = self.api.post("/api/v1/payouts/mpesa/timeout/wrong/", {}, format="json")
        self.assertEqual(res.status_code, 404)