"""
hardware/factory.py
====================
DESIGN PATTERN: Abstract Factory
----------------------------------
Creates families of kiosk components (Dispenser, Payment, InventoryPolicy)
for each kiosk type without specifying concrete classes.

Factory Structure:
  Abstract Factory -> KioskFactory
  Concrete Factories -> PharmacyKioskFactory, FoodKioskFactory, EmergencyKioskFactory
  Products -> IDispenser, IPaymentProvider, inventory policy string
"""

from abc import ABC, abstractmethod
from hardware.dispenser import (
    IDispenser, SpiralDispenser, RoboticArmDispenser, ConveyorDispenser
)


# ─── Abstract Factory ─────────────────────────────────────────────────────────

class KioskFactory(ABC):
    """
    Abstract Factory interface. Declares creation methods for a family of
    kiosk-specific components. Each concrete factory produces components
    compatible with a specific kiosk type.
    """

    @abstractmethod
    def create_dispenser(self) -> IDispenser:
        """Create the appropriate dispenser hardware for this kiosk type."""
        pass

    @abstractmethod
    def create_payment_config(self) -> dict:
        """Return payment configuration for this kiosk type."""
        pass

    @abstractmethod
    def create_inventory_policy(self) -> dict:
        """Return inventory policy settings for this kiosk type."""
        pass

    @abstractmethod
    def get_kiosk_type(self) -> str:
        pass


# ─── Concrete Factories ───────────────────────────────────────────────────────

class PharmacyKioskFactory(KioskFactory):
    """
    Concrete Factory for Pharmacy kiosks (e.g., hospital dispensaries).
    - Uses RoboticArmDispenser for precise medicine placement
    - Supports Credit Card + UPI payments
    - Enforces prescription-based inventory policy
    """

    def create_dispenser(self) -> IDispenser:
        print("  [PharmacyKioskFactory] Creating RoboticArmDispenser for pharmacy precision dispensing.")
        return RoboticArmDispenser(arm_id="pharma-arm-01")

    def create_payment_config(self) -> dict:
        return {
            "providers": ["CreditCard", "UPI"],
            "requires_id_verification": True,
            "prescription_check": True,
        }

    def create_inventory_policy(self) -> dict:
        return {
            "type": "PharmacyPolicy",
            "requires_refrigeration": True,
            "emergency_purchase_limit": 1,  # max 1 unit of controlled medicine
            "age_verification": True,
        }

    def get_kiosk_type(self) -> str:
        return "PharmacyKiosk"


class FoodKioskFactory(KioskFactory):
    """
    Concrete Factory for Food kiosks (e.g., metro stations, campuses).
    - Uses SpiralDispenser for packaged food items
    - Supports all payment methods
    - Standard inventory policy with bundle support
    """

    def create_dispenser(self) -> IDispenser:
        print("  [FoodKioskFactory] Creating SpiralDispenser for packaged food items.")
        return SpiralDispenser(motor_id=3)

    def create_payment_config(self) -> dict:
        return {
            "providers": ["CreditCard", "UPI", "DigitalWallet"],
            "requires_id_verification": False,
            "prescription_check": False,
        }

    def create_inventory_policy(self) -> dict:
        return {
            "type": "FoodPolicy",
            "requires_refrigeration": False,
            "emergency_purchase_limit": 5,
            "supports_bundles": True,
        }

    def get_kiosk_type(self) -> str:
        return "FoodKiosk"


class EmergencyKioskFactory(KioskFactory):
    """
    Concrete Factory for Emergency/Disaster Relief kiosks.
    - Uses ConveyorDispenser for fast bulk distribution
    - Cash-free, prioritises digital wallets
    - Strict emergency purchase limits enforced
    """

    def create_dispenser(self) -> IDispenser:
        print("  [EmergencyKioskFactory] Creating ConveyorDispenser for rapid emergency supply distribution.")
        return ConveyorDispenser(belt_speed=2.5)

    def create_payment_config(self) -> dict:
        return {
            "providers": ["DigitalWallet", "UPI"],
            "requires_id_verification": True,
            "free_distribution_mode": True,  # may override price to 0
        }

    def create_inventory_policy(self) -> dict:
        return {
            "type": "EmergencyPolicy",
            "requires_refrigeration": False,
            "emergency_purchase_limit": 2,  # per-user limit enforced strictly
            "priority_override": True,
        }

    def get_kiosk_type(self) -> str:
        return "EmergencyKiosk"
