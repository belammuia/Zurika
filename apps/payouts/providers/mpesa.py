import uuid

import requests
from django.conf import settings
from ..models import Payout
import base64

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

SANDBOX_URL = "https://sandbox.safaricom.co.ke"
PRODUCTION_URL = "https://api.safaricom.co.ke"

from .base import ProviderRejected, normalize_phone


class MpesaProvider:
    auto_settle = False  

    def reference_for(self, payout):
        return f"claims-{payout.pk}-{uuid.uuid4().hex[:12]}"

    @property
    def base(self):
        if getattr(settings, "MPESA_ENV", "sandbox") == "production":
            return PRODUCTION_URL
        return SANDBOX_URL


    def _callback_url(self, name):
        root = settings.MPESA_CALLBACK_BASE_URL.rstrip("/")
        return f"{root}/api/v1/payouts/mpesa/{name}/{settings.MPESA_CALLBACK_SECRET}/"

    def _get_access_token(self):
        try:
            r = requests.get(
                f"{self.base}/oauth/v1/generate",
                params={"grant_type": "client_credentials"},
                auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
                timeout=20,
            )
            r.raise_for_status()
            return r.json()["access_token"]
        except (requests.RequestException, KeyError, ValueError) as exc:
            raise ProviderRejected("Could not authenticate with M-Pesa") from exc

    def send(self, payout):
        payload = {
            "OriginatorConversationID": payout.provider_ref,
            "InitiatorName": settings.MPESA_INITIATOR_NAME,
            "SecurityCredential": settings.MPESA_SECURITY_CREDENTIAL,
            "CommandID": "BusinessPayment",
            "Amount": int(payout.amount),
            "PartyA": settings.MPESA_SHORTCODE,
            "PartyB": normalize_phone(payout.destination),
            "Remarks": f"Claim {payout.claim_id} payout",
            "QueueTimeOutURL": self._callback_url("timeout"),
            "ResultURL": self._callback_url("result"),
            "Occasion": f"claim-{payout.claim_id}",
        }

        r = requests.post(
            f"{self.base}/mpesa/b2c/v3/paymentrequest",
            json=payload,
            headers={"Authorization": f"Bearer {self._get_access_token()}"},
            timeout=50,
        )

        if 400 <= r.status_code < 500:
            raise ProviderRejected(r.text[:200]) 

        r.raise_for_status() 

        data = r.json()
        if str(data.get("ResponseCode")) != "0":
            raise ProviderRejected(data.get("ResponseDescription", "Rejected by M-Pesa"))
        
    def query_transaction_status(self, payout):
        """
        Submit an asynchronous Safaricom Transaction Status query.

        The returned response acknowledges the query; it is not
        the final status of the original payout.
        """
        payload = {
            "Initiator": settings.MPESA_INITIATOR_NAME,
            "SecurityCredential": settings.MPESA_SECURITY_CREDENTIAL,
            "CommandID": "TransactionStatusQuery",
            "OriginalConversationID": payout.provider_ref,
            "PartyA": settings.MPESA_SHORTCODE,
            "IdentifierType": "4",
            "ResultURL": self._callback_url("status-result"),
            "QueueTimeOutURL": self._callback_url("status-timeout"),
            "Remarks": f"Reconcile payout {payout.pk}",
            "Occasion": f"claim-{payout.claim_id}",
        }

        try:
            response = requests.post(
                f"{self.base}/mpesa/transactionstatus/v1/query",
                json=payload,
                headers={
                    "Authorization": (
                        f"Bearer {self._get_access_token()}"
                    ),
                },
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise ProviderRejected(
                "Could not submit transaction status query"
            ) from exc

        if str(data.get("ResponseCode")) != "0":
            raise ProviderRejected(
                data.get(
                    "ResponseDescription",
                    "Safaricom rejected the status query",
                )
            )

        return data
