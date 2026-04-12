"""
payment/payment.py
===================
DESIGN PATTERN: Adapter
------------------------
Converts incompatible payment provider APIs (UPI, Credit Card, Digital Wallet)
into a common IPaymentProvider interface. New providers can be added without
modifying existing code (Open/Closed Principle).

Adapter Structure:
  Target    -> IPaymentProvider (common interface)
  Adaptee   -> Legacy/third-party payment API classes (simulated)
  Adapter   -> UPIAdapter, CreditCardAdapter, DigitalWalletAdapter
  Abstract  -> PaymentAdapter (common adapter base)
"""

from abc import ABC, abstractmethod
from enum import Enum
import uuid
import csv
import os


class TransactionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED  = "FAILED"
    PENDING = "PENDING"
    REFUNDED = "REFUNDED"


# ─── Target Interface ─────────────────────────────────────────────────────────

class IPaymentProvider(ABC):
    """
    Target interface. All payment adapters expose this common interface.
    The rest of the system only depends on this interface, never on
    concrete gateway implementations.
    """

    @abstractmethod
    def process_payment(self, amount: float, reference: str) -> dict:
        """
        Process a payment of `amount` for `reference`.
        Returns: {"transaction_id": str, "status": TransactionStatus, "provider": str}
        """
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> dict:
        """
        Refund a previously processed transaction.
        Returns: {"transaction_id": str, "status": TransactionStatus}
        """
        pass

    @abstractmethod
    def get_status(self, transaction_id: str) -> TransactionStatus:
        """Query the current status of a transaction."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass


# ─── Simulated Third-Party APIs (Adaptees) ───────────────────────────────────

class _LegacyUPIGateway:
    """Simulated third-party UPI gateway with incompatible API."""

    def initiate_upi_transfer(self, vpa: str, rupees: float, note: str) -> str:
        """Returns a raw UPI reference string."""
        ref = f"UPI-{uuid.uuid4().hex[:8].upper()}"
        print(f"  [LegacyUPIGateway] Transfer ₹{rupees} to VPA={vpa}, note={note!r} → ref={ref}")
        return ref

    def check_upi_ref(self, ref: str) -> bool:
        return ref.startswith("UPI-")

    def raise_upi_dispute(self, ref: str) -> bool:
        print(f"  [LegacyUPIGateway] Dispute raised for ref={ref}")
        return True


class _LegacyCreditCardGateway:
    """Simulated credit card gateway with different API."""

    def charge_card(self, card_token: str, amount_paise: int, description: str) -> dict:
        """Returns raw gateway response dict (amount in paise, not rupees)."""
        charge_id = f"CHG-{uuid.uuid4().hex[:8].upper()}"
        print(f"  [LegacyCreditCardGateway] Charged ₹{amount_paise/100:.2f} on token={card_token} → {charge_id}")
        return {"charge_id": charge_id, "approved": True, "code": "00"}

    def reverse_charge(self, charge_id: str) -> bool:
        print(f"  [LegacyCreditCardGateway] Reversing charge {charge_id}")
        return True


class _LegacyDigitalWalletGateway:
    """Simulated digital wallet (e.g. Paytm/PhonePe) API."""

    def wallet_debit(self, wallet_id: str, amount: float) -> tuple:
        """Returns (success: bool, txn_ref: str)."""
        txn = f"WALLET-{uuid.uuid4().hex[:8].upper()}"
        print(f"  [LegacyDigitalWalletGateway] Debited ₹{amount} from wallet={wallet_id} → txn={txn}")
        return (True, txn)

    def wallet_credit(self, wallet_id: str, amount: float, original_txn: str) -> bool:
        print(f"  [LegacyDigitalWalletGateway] Credited ₹{amount} to wallet={wallet_id} (refund of {original_txn})")
        return True


# ─── Abstract Adapter Base ────────────────────────────────────────────────────

class PaymentAdapter(IPaymentProvider, ABC):
    """
    Abstract adapter base. Stores transaction records.
    Subclasses adapt specific payment gateways to IPaymentProvider.
    """

    def __init__(self):
        self._transactions: dict[str, dict] = {}

    def _record_transaction(self, txn_id: str, amount: float, status: TransactionStatus,
                             reference: str, raw_ref: str) -> dict:
        record = {
            "transaction_id": txn_id,
            "amount": amount,
            "status": status,
            "reference": reference,
            "raw_ref": raw_ref,
            "provider": self.get_provider_name(),
        }
        self._transactions[txn_id] = record
        return record

    def get_status(self, transaction_id: str) -> TransactionStatus:
        txn = self._transactions.get(transaction_id)
        return txn["status"] if txn else TransactionStatus.FAILED


# ─── Concrete Adapters ────────────────────────────────────────────────────────

class UPIAdapter(PaymentAdapter):
    """
    Adapter: Wraps _LegacyUPIGateway to expose IPaymentProvider.
    Converts the UPI-specific initiate_upi_transfer / raise_upi_dispute
    calls into standard process_payment / refund.
    """

    def __init__(self, vpa: str = "aura-kiosk@upi"):
        super().__init__()
        self._vpa = vpa
        self._gateway = _LegacyUPIGateway()  # adaptee

    def process_payment(self, amount: float, reference: str) -> dict:
        raw_ref = self._gateway.initiate_upi_transfer(self._vpa, amount, reference)
        txn_id = f"TXN-UPI-{uuid.uuid4().hex[:6].upper()}"
        return self._record_transaction(txn_id, amount, TransactionStatus.SUCCESS, reference, raw_ref)

    def refund(self, transaction_id: str) -> dict:
        txn = self._transactions.get(transaction_id)
        if not txn:
            return {"transaction_id": transaction_id, "status": TransactionStatus.FAILED}
        success = self._gateway.raise_upi_dispute(txn["raw_ref"])
        status = TransactionStatus.REFUNDED if success else TransactionStatus.FAILED
        txn["status"] = status
        return {"transaction_id": transaction_id, "status": status}

    def get_provider_name(self) -> str:
        return "UPI"


class CreditCardAdapter(PaymentAdapter):
    """
    Adapter: Wraps _LegacyCreditCardGateway.
    Converts paise-based charge API to standard rupee-based interface.
    """

    def __init__(self, card_token: str = "demo-card-token-xxxx"):
        super().__init__()
        self._card_token = card_token
        self._gateway = _LegacyCreditCardGateway()  # adaptee

    def process_payment(self, amount: float, reference: str) -> dict:
        amount_paise = int(amount * 100)  # API adaptation: rupees → paise
        response = self._gateway.charge_card(self._card_token, amount_paise, reference)
        txn_id = f"TXN-CC-{uuid.uuid4().hex[:6].upper()}"
        status = TransactionStatus.SUCCESS if response["approved"] else TransactionStatus.FAILED
        return self._record_transaction(txn_id, amount, status, reference, response["charge_id"])

    def refund(self, transaction_id: str) -> dict:
        txn = self._transactions.get(transaction_id)
        if not txn:
            return {"transaction_id": transaction_id, "status": TransactionStatus.FAILED}
        success = self._gateway.reverse_charge(txn["raw_ref"])
        status = TransactionStatus.REFUNDED if success else TransactionStatus.FAILED
        txn["status"] = status
        return {"transaction_id": transaction_id, "status": status}

    def get_provider_name(self) -> str:
        return "CreditCard"


class DigitalWalletAdapter(PaymentAdapter):
    """
    Adapter: Wraps _LegacyDigitalWalletGateway.
    Adapts tuple-based wallet_debit response to standard interface.
    """

    def __init__(self, wallet_id: str = "user-wallet-demo-001"):
        super().__init__()
        self._wallet_id = wallet_id
        self._gateway = _LegacyDigitalWalletGateway()  # adaptee

    def process_payment(self, amount: float, reference: str) -> dict:
        success, raw_ref = self._gateway.wallet_debit(self._wallet_id, amount)
        txn_id = f"TXN-WALL-{uuid.uuid4().hex[:6].upper()}"
        status = TransactionStatus.SUCCESS if success else TransactionStatus.FAILED
        return self._record_transaction(txn_id, amount, status, reference, raw_ref)

    def refund(self, transaction_id: str) -> dict:
        txn = self._transactions.get(transaction_id)
        if not txn:
            return {"transaction_id": transaction_id, "status": TransactionStatus.FAILED}
        success = self._gateway.wallet_credit(self._wallet_id, txn["amount"], txn["raw_ref"])
        status = TransactionStatus.REFUNDED if success else TransactionStatus.FAILED
        txn["status"] = status
        return {"transaction_id": transaction_id, "status": status}

    def get_provider_name(self) -> str:
        return "DigitalWallet"


# ─── Transaction Persistence ──────────────────────────────────────────────────

def persist_transaction(record: dict, filepath: str = "transactions.csv") -> None:
    """Append a transaction record to the CSV file."""
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["transaction_id", "provider", "amount", "status", "reference", "raw_ref"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "transaction_id": record.get("transaction_id", ""),
            "provider": record.get("provider", ""),
            "amount": record.get("amount", 0),
            "status": record.get("status", TransactionStatus.FAILED).value
                      if isinstance(record.get("status"), TransactionStatus)
                      else record.get("status", ""),
            "reference": record.get("reference", ""),
            "raw_ref": record.get("raw_ref", ""),
        })
