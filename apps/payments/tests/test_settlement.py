from .helpers import *  # noqa: F401,F403


class SettlePayoutTests(TestCase):

    def test_success_marks_paid(self):
        payout = make_payout(status="processing", ref="r1")

        settle_payout("r1", success=True)

        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PAID)

    def test_failure_records_reason(self):
        payout = make_payout(status="processing", ref="r1")

        settle_payout(
            "r1",
            success=False,
            reason="Insufficient funds",
        )

        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.FAILED)
        self.assertEqual(payout.failure_reason, "Insufficient funds")

    def test_second_settle_does_not_overwrite_paid(self):
        payout = make_payout(status="processing", ref="r1")

        settle_payout("r1", success=True)
        settle_payout("r1", success=False, reason="late duplicate")

        payout.refresh_from_db()
        self.assertEqual(payout.status, Payout.Status.PAID)


@override_settings(MPESA_CALLBACK_SECRET=SECRET)
class MpesaCallbackTests(TestCase):

    def setUp(self):
        self.api = APIClient()
        self.payout = make_payout(
            status="processing",
            ref="claims-1-abc",
        )

        self.result_url = f"/api/v1/payouts/mpesa/result/{SECRET}/"
        self.timeout_url = f"/api/v1/payouts/mpesa/timeout/{SECRET}/"
        self.status_result_url = (
            f"/api/v1/payouts/mpesa/status-result/{SECRET}/"
        )
        self.status_timeout_url = (
            f"/api/v1/payouts/mpesa/status-timeout/{SECRET}/"
        )

    def body(self, code, ref="claims-1-abc"):
        return {
            "Result": {
                "ResultCode": code,
                "ResultDesc": "x",
                "OriginatorConversationID": ref,
            }
        }

    def test_success_marks_paid(self):
        response = self.api.post(
            self.result_url, self.body(0), format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_failure_code_marks_failed(self):
        self.api.post(
            self.result_url, self.body(2001), format="json"
        )

        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.FAILED)

    def test_result_code_as_string_is_handled(self):
        self.api.post(
            self.result_url, self.body("0"), format="json"
        )

        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_duplicate_callback_does_not_overwrite_paid(self):
        self.api.post(
            self.result_url, self.body(0), format="json"
        )
        self.api.post(
            self.result_url, self.body(2001), format="json"
        )

        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_wrong_secret_is_404_and_changes_nothing(self):
        response = self.api.post(
            "/api/v1/payouts/mpesa/result/wrong/",
            self.body(0),
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.payout.refresh_from_db()
        self.assertEqual(
            self.payout.status, Payout.Status.PROCESSING
        )

    def test_unknown_reference_is_acknowledged_without_error(self):
        response = self.api.post(
            self.result_url, self.body(0, ref="nope"), format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(
            self.payout.status, Payout.Status.PROCESSING
        )

    def test_timeout_with_reference_marks_unknown(self):
        response = self.api.post(
            self.timeout_url,
            {
                "Result": {
                    "OriginatorConversationID": self.payout.provider_ref,
                    "ResultDesc": "Queue timeout",
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.UNKNOWN)

    def test_timeout_without_reference_does_not_change_payout(self):
        response = self.api.post(
            self.timeout_url, {"Result": {}}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(
            self.payout.status, Payout.Status.PROCESSING
        )

    def test_late_timeout_does_not_overwrite_paid(self):
        self.payout.status = Payout.Status.PAID
        self.payout.save(update_fields=["status"])

        self.api.post(
            self.timeout_url,
            {
                "Result": {
                    "OriginatorConversationID": self.payout.provider_ref,
                    "ResultDesc": "Late timeout",
                }
            },
            format="json",
        )

        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_late_timeout_does_not_overwrite_failed(self):
        self.payout.status = Payout.Status.FAILED
        self.payout.save(update_fields=["status"])

        self.api.post(
            self.timeout_url,
            {
                "Result": {
                    "OriginatorConversationID": self.payout.provider_ref,
                    "ResultDesc": "Late timeout",
                }
            },
            format="json",
        )

        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.FAILED)

    def test_timeout_with_wrong_secret_is_404(self):
        response = self.api.post(
            "/api/v1/payouts/mpesa/timeout/wrong/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_status_query_success_marks_paid(self):
        self.payout.status_query_ref = "query-ref-1"
        self.payout.save(update_fields=["status_query_ref"])

        response = self.api.post(
            self.status_result_url,
            {
                "Result": {
                    "OriginatorConversationID": "query-ref-1",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "ResultParameters": {
                        "ResultParameter": [
                            {
                                "Key": "TransactionStatus",
                                "Value": "Completed",
                            }
                        ]
                    },
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_inconclusive_status_query_marks_unknown(self):
        self.payout.status_query_ref = "query-ref-2"
        self.payout.save(update_fields=["status_query_ref"])

        response = self.api.post(
            self.status_result_url,
            {
                "Result": {
                    "OriginatorConversationID": "query-ref-2",
                    "ResultCode": 0,
                    "ResultDesc": "Query completed",
                    "ResultParameters": {
                        "ResultParameter": [
                            {
                                "Key": "TransactionStatus",
                                "Value": "Pending",
                            }
                        ]
                    },
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.UNKNOWN)

    def test_status_query_timeout_marks_unknown(self):
        self.payout.status_query_ref = "query-ref-3"
        self.payout.save(update_fields=["status_query_ref"])

        response = self.api.post(
            self.status_timeout_url,
            {
                "Result": {
                    "OriginatorConversationID": "query-ref-3",
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.UNKNOWN)

    def test_status_query_timeout_does_not_overwrite_paid(self):
        self.payout.status = Payout.Status.PAID
        self.payout.status_query_ref = "query-ref-4"
        self.payout.save(
            update_fields=["status", "status_query_ref"]
        )

        self.api.post(
            self.status_timeout_url,
            {
                "Result": {
                    "OriginatorConversationID": "query-ref-4",
                }
            },
            format="json",
        )

        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)

    def test_unknown_status_query_reference_is_acknowledged(self):
        response = self.api.post(
            self.status_result_url,
            {
                "Result": {
                    "OriginatorConversationID": "unknown-query",
                    "ResultCode": 0,
                    "ResultParameters": {
                        "ResultParameter": []
                    },
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.payout.refresh_from_db()
        self.assertEqual(
            self.payout.status, Payout.Status.PROCESSING
        )

    def test_duplicate_status_success_keeps_payout_paid(self):
        self.payout.status_query_ref = "query-ref-5"
        self.payout.save(update_fields=["status_query_ref"])

        body = {
            "Result": {
                "OriginatorConversationID": "query-ref-5",
                "ResultCode": 0,
                "ResultParameters": {
                    "ResultParameter": [
                        {
                            "Key": "TransactionStatus",
                            "Value": "Completed",
                        }
                    ]
                },
            }
        }

        self.api.post(
            self.status_result_url, body, format="json"
        )
        self.api.post(
            self.status_result_url, body, format="json"
        )

        self.payout.refresh_from_db()
        self.assertEqual(self.payout.status, Payout.Status.PAID)
