from .base import (
    BankProvider,
    BankTransferRequest,
    BankTransferResponse,
    TransferStatus
)
import requests
import base64
from django.conf import settings

class KCBBankProvider(BankProvider):

    def _get_token():
        try:
            auth_string = f"{settings.KCB_CONSUMER_KEY}:{settings.KCB_CONSUMER_SECRET}"
            b64_encode_string = base64.b64encode(auth_string.encode()).decode("utf-8")

            url = f"{settings.KCB_BUNI_BASE_URL}/token"
            headers={
                "Authorization": f"Basic {b64_encode_string}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            params={
                "grant_type": "client_credentials"
            }

            r = requests.post(url=url,headers=headers, params=params)
            r.raise_for_status()
            return r.json()["access_token"]
        except (requests.RequestException, ValueError,KeyError) as exp:
            raise Exception("Invalid/Expired tokens")
        

    def send_transfer(self, transfer):
        pass