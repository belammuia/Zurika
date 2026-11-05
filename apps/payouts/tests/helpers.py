
# apps/payouts/tests.py

from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
from model_bakery import baker
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.payouts.models import Payout
from apps.claims.models import Claim
from apps.payouts.payouts import settle_payout
from apps.payouts.providers import (
    MpesaProvider,
    ProviderRejected,
    get_provider,
    normalize_phone,
)
from apps.payouts.tasks import (
    choose_method,
    recover_stuck_payouts,
    send_payout,
)

SECRET = "test-secret-123"

MPESA_SETTINGS = {
    "MPESA_ENV": "sandbox",
    "MPESA_CONSUMER_KEY": "key",
    "MPESA_CONSUMER_SECRET": "secret",
    "MPESA_SHORTCODE": "600000",
    "MPESA_INITIATOR_NAME": "tester",
    "MPESA_SECURITY_CREDENTIAL": "cred",
    "MPESA_CALLBACK_BASE_URL": "https://example.ngrok-free.dev",
    "MPESA_CALLBACK_SECRET": SECRET,
}


# ---------- helpers ----------

def make_claim():
    return baker.make(
        "claims.Claim",
        status=Claim.Status.APPROVED,
        estimated_cost=Decimal("250.00"),
        insurer=baker.make("insurers.Insurer"),
    )

def make_payout(
    status="pending",
    amount="250.00",
    ref="",
    phone="0712345678",
):
    return Payout.objects.create(
        claim=make_claim(),
        amount=Decimal(amount),
        destination=phone,
        status=status,
        provider_ref=ref,
    )


def fake_response(status=200, body=None):
    response = MagicMock()
    response.status_code = status
    response.json.return_value = body or {}
    response.text = str(body)

    if status >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(
            f"{status}"
        )

    return response


# ---------- phone normalisation ----------
