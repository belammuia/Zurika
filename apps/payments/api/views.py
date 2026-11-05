
import hmac
import logging

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Payout
from ..services.payouts import settle_payout

logger = logging.getLogger(__name__)

ACK = {"ResultCode": 0, "ResultDesc": "Accepted"}
TIMEOUT_ACK = {"ResponseCode": "0", "ResponseDesc": "success"}

UNRESOLVED_STATUSES = (
    Payout.Status.PROCESSING,
    Payout.Status.UNKNOWN,
)


class _MpesaCallback(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def check_secret(self, secret):
        expected = getattr(settings, "MPESA_CALLBACK_SECRET", "")

        if not expected or not hmac.compare_digest(secret, expected):
            raise NotFound()


def _mark_unknown(provider_ref, reason):
    """Mark an unresolved payout UNKNOWN without overwriting a final status."""
    if not provider_ref:
        logger.warning("Callback received without a payout reference.")
        return

    with transaction.atomic():
        payout = (
            Payout.objects.select_for_update()
            .filter(provider_ref=provider_ref)
            .first()
        )

        if payout is None:
            logger.warning(
                "Callback for unknown payout reference %s",
                provider_ref,
            )
            return

        if payout.status not in UNRESOLVED_STATUSES:
            logger.info(
                "Ignoring timeout for payout %s with status %s",
                payout.pk,
                payout.status,
            )
            return

        payout.status = Payout.Status.UNKNOWN
        payout.failure_reason = str(reason)[:255]
        payout.save(
            update_fields=[
                "status",
                "failure_reason",
                "updated_at",
            ]
        )


def _result_parameters(result):
    """Convert Safaricom ResultParameter entries into a dictionary."""
    parameters = result.get("ResultParameters") or {}
    items = parameters.get("ResultParameter") or []

    if not isinstance(items, list):
        return {}

    return {
        item["Key"]: item.get("Value")
        for item in items
        if isinstance(item, dict) and item.get("Key")
    }


class MpesaResultView(_MpesaCallback):
    def post(self, request, secret):
        self.check_secret(secret)

        result = request.data.get("Result") or {}
        ref = result.get("OriginatorConversationID")

        if not ref:
            logger.warning("M-Pesa result callback has no reference.")
            return Response(ACK)

        success = str(result.get("ResultCode")) == "0"

        try:
            settle_payout(
                ref,
                success=success,
                reason=result.get("ResultDesc", "Payment failed."),
            )
        except Payout.DoesNotExist:
            logger.warning(
                "M-Pesa result for unknown payout reference %s",
                ref,
            )

        return Response(ACK)


class MpesaTimeoutView(_MpesaCallback):
    def post(self, request, secret):
        self.check_secret(secret)

        result = request.data.get("Result") or {}
        ref = result.get("OriginatorConversationID")
        reason = result.get(
            "ResultDesc",
            "The transaction timed out; outcome requires reconciliation.",
        )

        _mark_unknown(ref, reason)

        return Response(TIMEOUT_ACK, status=status.HTTP_200_OK)


class MpesaStatusResultView(_MpesaCallback):
    def post(self, request, secret):
        self.check_secret(secret)

        result = request.data.get("Result") or {}
        query_ref = result.get("OriginatorConversationID")

        if not query_ref:
            logger.warning(
                "Status-query result callback has no query reference."
            )
            return Response(ACK)

        payout = Payout.objects.filter(
            status_query_ref=query_ref
        ).first()

        if payout is None:
            logger.warning(
                "Status-query result for unknown query reference %s",
                query_ref,
            )
            return Response(ACK)

        # This is the status-query request's result code, not
        # necessarily the original payment's result.
        if str(result.get("ResultCode")) != "0":
            logger.warning(
                "Status query for payout %s was inconclusive: %s",
                payout.pk,
                result.get("ResultDesc", ""),
            )
            return Response(ACK)

        parameters = _result_parameters(result)
        transaction_status = str(
            parameters.get("TransactionStatus", "")
        ).strip().lower()

        # Only use these mappings after verifying the actual Daraja
        # sandbox result values and payload structure.
        if transaction_status in {"completed", "complete", "success"}:
            settle_payout(payout.provider_ref, success=True)

        elif transaction_status in {
            "cancelled",
            "canceled",
            "declined",
            "expired",
        }:
            settle_payout(
                payout.provider_ref,
                success=False,
                reason=f"Transaction status: {transaction_status}",
            )

        else:
            # Missing, pending, or unrecognised status: don't guess.
            _mark_unknown(
                payout.provider_ref,
                f"Status query inconclusive: {transaction_status or 'missing status'}",
            )

        return Response(ACK)


class MpesaStatusTimeoutView(_MpesaCallback):
    def post(self, request, secret):
        self.check_secret(secret)

        result = request.data.get("Result") or {}
        query_ref = result.get("OriginatorConversationID")

        if not query_ref:
            logger.warning(
                "Status-query timeout callback has no query reference."
            )
            return Response(TIMEOUT_ACK)

        payout = Payout.objects.filter(
            status_query_ref=query_ref
        ).first()

        if payout is None:
            logger.warning(
                "Status-query timeout for unknown query reference %s",
                query_ref,
            )
        else:
            _mark_unknown(
                payout.provider_ref,
                "Transaction status query timed out; outcome remains unknown.",
            )

        return Response(TIMEOUT_ACK, status=status.HTTP_200_OK)
