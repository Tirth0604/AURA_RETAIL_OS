"""
core/kiosk.py
==============
DESIGN PATTERNS: Command, Singleton, Facade
--------------------------------------------
Command:
  Encapsulates each operation as an object with execute(), undo(), log().
  Enables transaction history and atomic rollback.

  Interface  -> IKioskCommand
  Commands   -> PurchaseItemCommand, RefundCommand, RestockCommand

Singleton:
  CentralRegistry – single global instance for config and system status.

Facade:
  KioskInterface – single entry point hiding all subsystem complexity.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import json
import os


# ─── Singleton: CentralRegistry ───────────────────────────────────────────────

class CentralRegistry:
    """
    DESIGN PATTERN: Singleton
    Stores global system configuration and kiosk status.
    Accessible across all subsystems. Only one instance ever exists.
    """

    _instance: Optional["CentralRegistry"] = None

    def __new__(cls) -> "CentralRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
            cls._instance._kiosk_statuses = {}
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, config_path: str = "config.json") -> None:
        if self._initialized:
            return
        if os.path.exists(config_path):
            with open(config_path) as f:
                self._config = json.load(f)
        else:
            self._config = {
                "kiosk_id": "AURA-001",
                "mode": "active",
                "emergency_purchase_limit": 2,
                "version": "2.0-subtask2",
            }
        self._initialized = True
        print(f"  [CentralRegistry] Initialized. Kiosk ID: {self._config.get('kiosk_id')}")

    def get_config(self, key: str, default=None):
        return self._config.get(key, default)

    def set_status(self, kiosk_id: str, status: dict) -> None:
        self._kiosk_statuses[kiosk_id] = status

    def get_status(self, kiosk_id: str) -> dict:
        return self._kiosk_statuses.get(kiosk_id, {})

    def get_instance(self) -> "CentralRegistry":
        return self


# ─── Command Interface ────────────────────────────────────────────────────────

class IKioskCommand(ABC):
    """
    Command interface. Every kiosk operation is modelled as a Command,
    enabling execute, undo, and log operations for atomic transactions.
    """

    @abstractmethod
    def execute(self) -> bool:
        pass

    @abstractmethod
    def undo(self) -> bool:
        pass

    @abstractmethod
    def log(self) -> str:
        pass


# ─── Concrete Commands ────────────────────────────────────────────────────────

class PurchaseItemCommand(IKioskCommand):
    """
    Command: Encapsulates a purchase operation.
    execute() → process payment → dispense item → reduce stock
    undo()    → refund payment → retract item → restore stock
    Implements Atomic Transaction constraint.
    """

    def __init__(self, kiosk, item_name: str, quantity: int, payment_provider):
        self._kiosk = kiosk
        self._item_name = item_name
        self._quantity = quantity
        self._provider = payment_provider
        self._transaction_record = None
        self._executed = False

    def execute(self) -> bool:
        print(f"\n  [PurchaseItemCommand] Executing purchase: {self._quantity}x '{self._item_name}'")

        # 1. Check inventory via proxy
        item = self._kiosk.inventory.get_item(self._item_name, role="kiosk")
        if not item or not item.is_available():
            print(f"  [PurchaseItemCommand] FAILED: '{self._item_name}' unavailable.")
            return False
        if item.get_stock() < self._quantity:
            print(f"  [PurchaseItemCommand] FAILED: Insufficient stock.")
            return False

        # 2. Emergency purchase limit check (Path B system constraint)
        registry = CentralRegistry()
        if registry.get_config("mode") == "emergency":
            limit = registry.get_config("emergency_purchase_limit", 2)
            if self._quantity > limit:
                print(f"  [PurchaseItemCommand] FAILED: Emergency limit is {limit} units.")
                return False

        total = round(item.get_price() * self._quantity, 2)

        # 3. Process payment (via Adapter)
        self._transaction_record = self._provider.process_payment(
            total, f"purchase:{self._item_name}:qty={self._quantity}"
        )
        from payment.payment import TransactionStatus, persist_transaction
        if self._transaction_record["status"] != TransactionStatus.SUCCESS:
            print(f"  [PurchaseItemCommand] FAILED: Payment failed.")
            return False

        # 4. Dispense item (via Bridge)
        dispensed = self._kiosk.dispenser.dispense_item(self._item_name)
        if not dispensed:
            # Atomic rollback: refund payment
            print(f"  [PurchaseItemCommand] Dispense failed. Rolling back payment...")
            self._provider.refund(self._transaction_record["transaction_id"])
            return False

        # 5. Update inventory (Inventory Consistency Constraint: only on success)
        self._kiosk.inventory.update_stock(self._item_name, -self._quantity, role="kiosk")

        # 6. Persist transaction
        persist_transaction(self._transaction_record)

        self._executed = True
        print(f"  [PurchaseItemCommand] SUCCESS. TXN: {self._transaction_record['transaction_id']}")
        return True

    def undo(self) -> bool:
        if not self._executed or not self._transaction_record:
            print("  [PurchaseItemCommand] Nothing to undo.")
            return False
        print(f"  [PurchaseItemCommand] Undoing purchase of '{self._item_name}'...")

        # Refund payment
        self._provider.refund(self._transaction_record["transaction_id"])

        # Retract item
        self._kiosk.dispenser.retract_item(self._item_name)

        # Restore stock
        self._kiosk.inventory.update_stock(self._item_name, self._quantity, role="kiosk")

        self._executed = False
        return True

    def log(self) -> str:
        txn_id = self._transaction_record["transaction_id"] if self._transaction_record else "N/A"
        return (
            f"PurchaseItemCommand | item={self._item_name} qty={self._quantity} "
            f"executed={self._executed} txn={txn_id}"
        )


class RefundCommand(IKioskCommand):
    """Command: Encapsulates a refund operation."""

    def __init__(self, payment_provider, transaction_id: str):
        self._provider = payment_provider
        self._transaction_id = transaction_id
        self._result = None

    def execute(self) -> bool:
        print(f"  [RefundCommand] Processing refund for TXN: {self._transaction_id}")
        self._result = self._provider.refund(self._transaction_id)
        from payment.payment import TransactionStatus
        success = self._result["status"] == TransactionStatus.REFUNDED
        print(f"  [RefundCommand] {'SUCCESS' if success else 'FAILED'}")
        return success

    def undo(self) -> bool:
        print("  [RefundCommand] Refunds cannot be undone.")
        return False

    def log(self) -> str:
        return f"RefundCommand | txn={self._transaction_id} result={self._result}"


class RestockCommand(IKioskCommand):
    """Command: Encapsulates a restock operation."""

    def __init__(self, inventory_proxy, item_name: str, quantity: int):
        self._inventory = inventory_proxy
        self._item_name = item_name
        self._quantity = quantity
        self._executed = False

    def execute(self) -> bool:
        print(f"  [RestockCommand] Restocking '{self._item_name}' +{self._quantity}")
        success = self._inventory.update_stock(self._item_name, self._quantity, role="admin")
        self._executed = success
        return success

    def undo(self) -> bool:
        if not self._executed:
            return False
        print(f"  [RestockCommand] Undoing restock of '{self._item_name}' -{self._quantity}")
        return self._inventory.update_stock(self._item_name, -self._quantity, role="admin")

    def log(self) -> str:
        return f"RestockCommand | item={self._item_name} qty={self._quantity} executed={self._executed}"


# ─── AuraKiosk Core ───────────────────────────────────────────────────────────

class AuraKiosk:
    """
    Central kiosk class that owns and coordinates all subsystems.
    Used by KioskInterface (Facade). Not directly accessed externally.
    """

    def __init__(self, kiosk_id: str, dispenser, inventory, payment_provider, hardware_module=None):
        self.kiosk_id = kiosk_id
        self.dispenser = dispenser              # Bridge abstraction
        self.inventory = inventory              # InventoryProxy
        self.payment = payment_provider         # IPaymentProvider (Adapter)
        self.hardware_module = hardware_module  # HardwareModule (Decorator chain)
        self._command_history: List[IKioskCommand] = []

        # Register with CentralRegistry
        registry = CentralRegistry()
        registry.set_status(kiosk_id, {"status": "online", "hardware": dispenser.get_status()})

    def execute_command(self, command: IKioskCommand) -> bool:
        result = command.execute()
        self._command_history.append(command)
        return result

    def undo_last_command(self) -> bool:
        if not self._command_history:
            print("  [AuraKiosk] No commands to undo.")
            return False
        return self._command_history[-1].undo()

    def get_status(self) -> dict:
        """Derived attribute: operational status computed from hardware + mode."""
        registry = CentralRegistry()
        hw_status = self.dispenser.get_status()
        hw_module_status = self.hardware_module.get_status() if self.hardware_module else {}
        return {
            "kiosk_id": self.kiosk_id,
            "mode": registry.get_config("mode", "active"),
            "dispenser": hw_status,
            "hardware_modules": hw_module_status,
            "command_history_count": len(self._command_history),
        }

    def add_module(self, module_class, **kwargs):
        """Dynamically attach a hardware decorator module at runtime."""
        from hardware.modules import HardwareModule
        if self.hardware_module is None:
            from hardware.modules import BaseKioskHardware
            self.hardware_module = BaseKioskHardware()
        self.hardware_module = module_class(self.hardware_module, **kwargs)
        print(f"  [AuraKiosk] Module added. Active stack: {self.hardware_module.get_module_name()}")


# ─── Facade: KioskInterface ───────────────────────────────────────────────────

class KioskInterface:
    """
    DESIGN PATTERN: Facade
    Single entry point for all external interactions with the kiosk.
    Hides internal subsystem complexity (Inventory, Payment, Hardware, Commands).
    """

    def __init__(self, kiosk: AuraKiosk):
        self._kiosk = kiosk

    def purchase_item(self, item_name: str, quantity: int = 1) -> bool:
        """External-facing purchase operation. Delegates to PurchaseItemCommand."""
        print(f"\n[KioskInterface] purchase_item('{item_name}', qty={quantity})")
        cmd = PurchaseItemCommand(self._kiosk, item_name, quantity, self._kiosk.payment)
        return self._kiosk.execute_command(cmd)

    def refund_transaction(self, transaction_id: str) -> bool:
        """External-facing refund operation."""
        print(f"\n[KioskInterface] refund_transaction('{transaction_id}')")
        cmd = RefundCommand(self._kiosk.payment, transaction_id)
        return self._kiosk.execute_command(cmd)

    def restock_inventory(self, item_name: str, quantity: int) -> bool:
        """External-facing restock operation (admin use)."""
        print(f"\n[KioskInterface] restock_inventory('{item_name}', qty={quantity})")
        cmd = RestockCommand(self._kiosk.inventory, item_name, quantity)
        return self._kiosk.execute_command(cmd)

    def run_diagnostics(self) -> dict:
        """External-facing diagnostics. Returns derived operational status."""
        print(f"\n[KioskInterface] run_diagnostics()")
        status = self._kiosk.get_status()
        print(f"  [KioskInterface] Kiosk Status: {json.dumps(status, indent=4)}")
        return status

    def list_inventory(self) -> list:
        """External-facing inventory listing."""
        print(f"\n[KioskInterface] list_inventory()")
        items = self._kiosk.inventory.list_items(role="kiosk")
        for item in items:
            print(f"  • {item}")
        return items
