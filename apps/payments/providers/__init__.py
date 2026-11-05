from ..models import Payout
from .base import ProviderRejected, normalize_phone
from .fake import FakeProvider
from .mpesa import MpesaProvider, SANDBOX_URL, PRODUCTION_URL


def get_provider(method):
    if method == Payout.Payment_Method.MPESA:
        return MpesaProvider()

    if method == Payout.Payment_Method.BANK:
        raise ProviderRejected(
            "Bank provider is not implemented yet."
        )

    raise ProviderRejected(
        f"Unsupported payment method: {method}"
    )
