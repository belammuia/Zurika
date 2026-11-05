from .helpers import *  # noqa: F401,F403


class NormalizePhoneTests(TestCase):

    def test_local_format(self):
        self.assertEqual(
            normalize_phone("0712345678"),
            "254712345678",
        )

    def test_plus_international(self):
        self.assertEqual(
            normalize_phone("+254712345678"),
            "254712345678",
        )

    def test_already_normalised(self):
        self.assertEqual(
            normalize_phone("254712345678"),
            "254712345678",
        )

    def test_spaces_and_dashes_are_stripped(self):
        self.assertEqual(
            normalize_phone("0712-345 678"),
            "254712345678",
        )

    def test_too_short_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            normalize_phone("12345")

    def test_wrong_country_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            normalize_phone("256712345678")


class GetProviderTests(TestCase):

    def test_mpesa_method_returns_mpesa_provider(self):
        self.assertIsInstance(
            get_provider(Payout.Payment_Method.MPESA),
            MpesaProvider,
        )

    def test_bank_method_is_rejected_until_implemented(self):
        with self.assertRaises(ProviderRejected):
            get_provider(Payout.Payment_Method.BANK)

    def test_unknown_method_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            get_provider("unsupported")


@override_settings(**MPESA_SETTINGS)
class MpesaProviderTests(TestCase):

    def send(self, response=None, side_effect=None):
        payout = make_payout(
            status="processing",
            ref="claims-1-abc",
        )

        with (
            patch.object(
                MpesaProvider,
                "_get_access_token",
                return_value="tok",
            ),
            patch(
                "apps.payouts.providers.mpesa.requests.post",
                return_value=response,
                side_effect=side_effect,
            ) as post,
        ):
            MpesaProvider().send(payout)

        return payout, post

    def test_references_are_unique_and_carry_no_personal_data(self):
        payout = make_payout()
        provider = MpesaProvider()

        first = provider.reference_for(payout)
        second = provider.reference_for(payout)

        self.assertNotEqual(first, second)
        self.assertTrue(first.startswith(f"claims-{payout.pk}-"))

    def test_accepted_request_has_correct_payload(self):
        _, post = self.send(
            fake_response(200, {"ResponseCode": "0"})
        )

        payload = post.call_args.kwargs["json"]

        self.assertEqual(
            payload["OriginatorConversationID"],
            "claims-1-abc",
        )
        self.assertEqual(payload["PartyB"], "254712345678")
        self.assertEqual(payload["Amount"], 250)
        self.assertEqual(payload["CommandID"], "BusinessPayment")
        self.assertEqual(payload["PartyA"], "600000")

        self.assertIn(SECRET, payload["ResultURL"])
        self.assertIn(SECRET, payload["QueueTimeOutURL"])
        self.assertTrue(
            payload["ResultURL"].startswith(
                "https://example.ngrok-free.dev/"
            )
        )

    def test_uses_sandbox_url_and_v3_endpoint(self):
        _, post = self.send(
            fake_response(200, {"ResponseCode": "0"})
        )

        self.assertEqual(
            post.call_args.args[0],
            "https://sandbox.safaricom.co.ke/"
            "mpesa/b2c/v3/paymentrequest",
        )

    @override_settings(MPESA_ENV="production")
    def test_production_env_uses_production_url(self):
        _, post = self.send(
            fake_response(200, {"ResponseCode": "0"})
        )

        self.assertTrue(
            post.call_args.args[0].startswith(
                "https://api.safaricom.co.ke/"
            )
        )

    def test_nonzero_response_code_is_rejected(self):
        with self.assertRaises(ProviderRejected):
            self.send(
                fake_response(
                    200,
                    {
                        "ResponseCode": "1",
                        "ResponseDescription": "No",
                    },
                )
            )

    def test_4xx_is_a_definite_rejection(self):
        with self.assertRaises(ProviderRejected):
            self.send(
                fake_response(
                    400,
                    {"errorMessage": "bad request"},
                )
            )

    def test_5xx_is_not_swallowed_by_provider(self):
        with self.assertRaises(requests.HTTPError):
            self.send(fake_response(503))

    def test_timeout_is_not_swallowed_by_provider(self):
        with self.assertRaises(requests.Timeout):
            self.send(side_effect=requests.Timeout())

    def test_invalid_phone_is_rejected_before_payment_request(self):
        payout = make_payout(
            status="processing",
            ref="r1",
            phone="123",
        )

        with (
            patch.object(
                MpesaProvider,
                "_get_access_token",
                return_value="tok",
            ),
            patch(
                "apps.payouts.providers.mpesa.requests.post"
            ) as post,
        ):
            with self.assertRaises(ProviderRejected):
                MpesaProvider().send(payout)

        post.assert_not_called()

    def test_auth_failure_is_a_definite_rejection(self):
        with patch(
            "apps.payouts.providers.mpesa.requests.get",
            side_effect=requests.ConnectionError(),
        ):
            with self.assertRaises(ProviderRejected):
                MpesaProvider()._get_access_token()
