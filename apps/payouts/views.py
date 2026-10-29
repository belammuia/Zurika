import hmac
import logging

from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payout
from .payouts import settle_payout

logger = logging.getLogger(__name__)

ACK = {"ResultCode": 0, "ResultDesc": "Accepted"}


class _MpesaCallback(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def check_secret(self, secret):
        expected = getattr(settings, "MPESA_CALLBACK_SECRET", "")
        
        if not expected or not hmac.compare_digest(secret, expected):
            raise NotFound()


class MpesaResultView(_MpesaCallback):
    def post(self, request, secret):
        self.check_secret(secret)

        result = request.data.get("Result", {})
        ref = result.get("OriginatorConversationID")
        success = str(result.get("ResultCode")) == "0"

        try:
            settle_payout(ref, success=success, reason=result.get("ResultDesc", ""))
        except Payout.DoesNotExist:
            logger.warning("M-Pesa result for unknown payout ref %s", ref)

        return Response(ACK)


class MpesaTimeoutView(_MpesaCallback):
    def post(self, request, secret):
        self.check_secret(secret)
        # The outcome is unknown, so leave the payout "processing" for reconciliation.
        logger.warning("M-Pesa timeout callback received")
        return Response(ACK)