from .base import (
    BankProvider,
    BankTransferRequest,
    BankTransferResponse,
    TransferStatus,
)

class FakeBankProvider(BankProvider):

    def send_transfer(
        self,
        transfer: BankTransferRequest,
    ) -> BankTransferResponse:

        return BankTransferResponse(
            status=TransferStatus.SUCCESS,
            provider_reference=f"FAKE-BANK-{transfer.reference}",
            message="Simulated bank transfer accepted.",
        )

    def check_transfer_status(
        self,
        reference: str,
    ) -> BankTransferResponse:

        return BankTransferResponse(
            status=TransferStatus.SUCCESS,
            provider_reference=reference,
            message="Simulated transfer completed.",
        )