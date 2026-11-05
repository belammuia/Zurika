from .helpers import *  # noqa: F401,F403


class ChooseMethodTests(TestCase):

    def test_amount_below_limit_uses_mpesa(self):
        self.assertEqual(
            choose_method(Decimal("100000.00")),
            Payout.Payment_Method.MPESA,
        )

    def test_amount_at_limit_uses_mpesa(self):
        self.assertEqual(
            choose_method(Decimal("250000.00")),
            Payout.Payment_Method.MPESA,
        )

    def test_amount_above_limit_uses_bank(self):
        self.assertEqual(
            choose_method(Decimal("250000.01")),
            Payout.Payment_Method.BANK,
        )

    def test_large_amount_uses_bank(self):
        self.assertEqual(
            choose_method(Decimal("300000.00")),
            Payout.Payment_Method.BANK,
        )


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

        with patch(
            "apps.payouts.tasks.get_provider",
            return_value=provider,
        ):
            send_payout(payout.pk)

        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PROCESSING)
        self.assertEqual(payout.provider_ref, "ref-1")
        self.assertEqual(payout.attempts, 1)
        provider.send.assert_called_once()

    def test_reference_is_saved_before_the_send(self):
        payout = make_payout()
        seen = {}

        def check(provider_payout):
            saved = Payout.objects.get(pk=provider_payout.pk)
            seen["ref"] = saved.provider_ref

        provider = self.mock_provider(send_side_effect=check)

        with patch(
            "apps.payouts.tasks.get_provider",
            return_value=provider,
        ):
            send_payout(payout.pk)

        self.assertEqual(seen["ref"], "ref-1")

    def test_definite_rejection_marks_failed(self):
        payout = make_payout()
        provider = self.mock_provider(
            send_side_effect=ProviderRejected("invalid number")
        )

        with patch(
            "apps.payouts.tasks.get_provider",
            return_value=provider,
        ):
            send_payout(payout.pk)

        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.FAILED)
        self.assertEqual(payout.failure_reason, "invalid number")

    def test_uncertain_failure_marks_unknown(self):
        payout = make_payout()
        provider = self.mock_provider(
            send_side_effect=requests.Timeout()
        )

        with patch(
            "apps.payouts.tasks.get_provider",
            return_value=provider,
        ):
            send_payout(payout.pk)

        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.UNKNOWN)
        self.assertIn("uncertain", payout.failure_reason.lower())
        self.assertEqual(payout.attempts, 1)

    def test_running_the_task_twice_sends_once(self):
        payout = make_payout()
        provider = self.mock_provider()

        with patch(
            "apps.payouts.tasks.get_provider",
            return_value=provider,
        ):
            send_payout(payout.pk)
            send_payout(payout.pk)

        provider.send.assert_called_once()
        payout.refresh_from_db()
        self.assertEqual(payout.attempts, 1)

    def test_uncertain_payout_is_not_resent_by_a_retry(self):
        payout = make_payout()
        provider = self.mock_provider(
            send_side_effect=requests.Timeout()
        )

        with patch(
            "apps.payouts.tasks.get_provider",
            return_value=provider,
        ):
            send_payout(payout.pk)
            send_payout(payout.pk)

        provider.send.assert_called_once()
        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.UNKNOWN)
        self.assertEqual(payout.attempts, 1)

    def test_auto_settle_provider_ends_paid(self):
        payout = make_payout()
        provider = self.mock_provider(auto_settle=True)

        with patch(
            "apps.payouts.tasks.get_provider",
            return_value=provider,
        ):
            send_payout(payout.pk)

        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PAID)

    def test_large_amount_without_bank_provider_fails_cleanly(self):
        payout = make_payout(amount="300000.00")

        send_payout(payout.pk)

        payout.refresh_from_db()
        self.assertEqual(payout.method, Payout.Payment_Method.BANK)
        self.assertEqual(payout.status, Payout.Status.FAILED)
        self.assertIn("bank", payout.failure_reason.lower())


class RecoverStuckPayoutsTests(TestCase):

    def age(self, payout, minutes):
        from datetime import timedelta
        from django.utils import timezone

        past = timezone.now() - timedelta(minutes=minutes)

        Payout.objects.filter(pk=payout.pk).update(
            created_at=past,
            updated_at=past,
        )

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
