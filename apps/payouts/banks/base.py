from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class TransferStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BankTransferRequest:
    reference: str
    amount: Decimal
    currency: str
    beneficiary_name: str
    beneficiary_account: str
    bank_code: str
    narration: str = ""


@dataclass(frozen=True)
class BankTransferResponse:
    status: TransferStatus
    provider_reference: str = ""
    message: str = ""


class BankProvider(ABC):

    @abstractmethod
    def send_transfer(
        self,
        transfer: BankTransferRequest,
    ) -> BankTransferResponse:
        pass

    @abstractmethod
    def check_transfer_status(
        self,
        reference: str,
    ) -> BankTransferResponse:
        pass