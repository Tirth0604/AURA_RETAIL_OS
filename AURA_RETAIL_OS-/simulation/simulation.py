"""
simulation/simulation.py
=========================
Aura Retail OS – Path B Simulation
Demonstrates all implemented design patterns through three scenarios:

  Scenario 1: Normal purchase flow (Facade + Command + Adapter + Bridge + Proxy + Composite)
  Scenario 2: Hardware replacement at runtime (Bridge pattern – Path B §5.2.3)
  Scenario 3: Adding new hardware modules dynamically (Decorator pattern)

Run from /aura_retail_os/:  python simulation/simulation.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.kiosk import CentralRegistry, AuraKiosk, KioskInterface
from hardware.dispenser import Dispenser, SpiralDispenser, RoboticArmDispenser, ConveyorDispenser
from hardware.modules import BaseKioskHardware, RefrigerationModule, SolarMonitoringModule, NetworkModule
from hardware.factory import FoodKioskFactory, PharmacyKioskFactory, EmergencyKioskFactory
from inventory.inventory import InventoryProxy, Product, ProductBundle
from payment.payment import UPIAdapter, CreditCardAdapter, DigitalWalletAdapter


# ─── Helpers ──────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")


def subsection(title: str) -> None:
    print(f"\n  ── {title}")


# ─── Scenario 1: Normal Purchase Flow ────────────────────────────────────────

def scenario_1_normal_purchase():
    section("SCENARIO 1: Normal Purchase Flow (Food Kiosk)")
    print("  Patterns demonstrated: Abstract Factory, Facade, Command,")
    print("  Adapter (UPI), Bridge (Spiral), Composite, Proxy")

    # Abstract Factory creates kiosk family
    subsection("1a. Creating kiosk components via Abstract Factory")
    factory = FoodKioskFactory()
    hw_impl = factory.create_dispenser()
    policy  = factory.create_inventory_policy()
    payment_cfg = factory.create_payment_config()
    print(f"  Kiosk type      : {factory.get_kiosk_type()}")
    print(f"  Payment config  : {payment_cfg}")
    print(f"  Inventory policy: {policy}")

    # Bridge: wrap hardware in abstraction
    dispenser = Dispenser(hw_impl)

    # Inventory: Composite + Proxy
    subsection("1b. Setting up Composite inventory via InventoryProxy")
    proxy = InventoryProxy()

    # Leaf products
    chips   = Product("Lays Chips",       price=20.0,  stock=10)
    water   = Product("Water Bottle",     price=15.0,  stock=20)
    granola = Product("Granola Bar",      price=35.0,  stock=5)
    juice   = Product("Orange Juice",     price=40.0,  stock=8,
                      requires_refrigeration=True, refrigeration_available=True)

    # Composite bundle (snack + drink)
    snack_bundle = ProductBundle("Snack Combo", discount_pct=0.10)
    snack_bundle.add_item(chips)
    snack_bundle.add_item(water)

    # Nested bundle
    mega_bundle = ProductBundle("Mega Refresh Bundle", discount_pct=0.15)
    mega_bundle.add_item(snack_bundle)
    mega_bundle.add_item(juice)

    for item in [chips, water, granola, juice, snack_bundle, mega_bundle]:
        proxy.add_item(item, role="admin")

    # Adapter: UPI payment
    payment = UPIAdapter()

    # CentralRegistry singleton
    registry = CentralRegistry()
    registry.initialize()

    # AuraKiosk
    kiosk = AuraKiosk("AURA-FOOD-01", dispenser, proxy, payment)

    # Hardware modules via Decorator
    kiosk.add_module(NetworkModule, ssid="AuraNet-5G")
    kiosk.add_module(RefrigerationModule, target_temp_celsius=4.0)

    # KioskInterface Facade
    facade = KioskInterface(kiosk)

    subsection("1c. Listing inventory")
    facade.list_inventory()

    subsection("1d. Purchasing 'Lays Chips' via Facade")
    success = facade.purchase_item("Lays Chips", quantity=2)
    print(f"  Purchase result: {'✓ Success' if success else '✗ Failed'}")

    subsection("1e. Running diagnostics")
    facade.run_diagnostics()

    subsection("1f. Attempting guest access to inventory (Proxy denial)")
    denied = proxy.list_items(role="guest")
    print(f"  Guest list result (expect DENIED): {denied}")

    subsection("1g. Restocking Granola Bar")
    facade.restock_inventory("Granola Bar", quantity=10)

    return facade, kiosk, proxy


# ─── Scenario 2: Runtime Hardware Replacement ─────────────────────────────────

def scenario_2_hardware_replacement():
    section("SCENARIO 2: Runtime Hardware Replacement (Path B §5.2.3)")
    print("  Pattern demonstrated: Bridge – swap implementor without")
    print("  modifying high-level dispensing logic.")

    # Start with SpiralDispenser
    spiral   = SpiralDispenser(motor_id=1)
    dispenser = Dispenser(spiral)

    print("\n  Initial hardware:")
    dispenser.run_calibration()
    dispenser.dispense_item("Test Item")

    # Simulate hardware failure → replace with RoboticArmDispenser at runtime
    print("\n  [Simulation] Motor failure detected! Replacing hardware module...")
    robotic = RoboticArmDispenser(arm_id="backup-arm-02")
    dispenser.replace_hardware(robotic)

    print("\n  After replacement (same high-level calls, new hardware):")
    dispenser.run_calibration()
    dispenser.dispense_item("Test Item")

    # Replace again with Conveyor
    print("\n  [Simulation] Switching to conveyor for emergency bulk mode...")
    conveyor = ConveyorDispenser(belt_speed=3.0)
    dispenser.replace_hardware(conveyor)
    dispenser.dispense_item("Emergency Supplies")

    print("\n  [Bridge] High-level logic never changed – only the implementor was swapped.")


# ─── Scenario 3: Dynamic Module Attachment ────────────────────────────────────

def scenario_3_dynamic_modules():
    section("SCENARIO 3: Dynamic Hardware Module Attachment (Decorator)")
    print("  Pattern demonstrated: Decorator – attach optional modules")
    print("  at runtime without modifying the base kiosk class.")

    base = BaseKioskHardware()
    print(f"\n  Base hardware: {base.get_module_name()}")
    print(f"  Status: {base.get_status()}")

    # Add Network module
    with_network = NetworkModule(base, ssid="AuraNet-5G")
    print(f"\n  After NetworkModule: {with_network.get_module_name()}")
    print(f"  Operate: {with_network.operate()}")

    # Add Refrigeration on top
    with_fridge = RefrigerationModule(with_network, target_temp_celsius=2.0)
    print(f"\n  After RefrigerationModule: {with_fridge.get_module_name()}")
    print(f"  Operate: {with_fridge.operate()}")

    # Add Solar on top
    with_solar = SolarMonitoringModule(with_fridge)
    print(f"\n  After SolarMonitoringModule: {with_solar.get_module_name()}")
    print(f"  Operate: {with_solar.operate()}")
    print(f"\n  Full status: {with_solar.get_status()}")

    # Simulate refrigeration going offline → product becomes unavailable
    print("\n  [Simulation] Refrigeration module goes offline...")
    cold_item = Product("Cold Medicine", price=120.0, stock=5,
                        requires_refrigeration=True, refrigeration_available=True)
    print(f"  Before: {cold_item}")
    cold_item.set_refrigeration_available(False)
    print(f"  After refrigeration loss: {cold_item}")
    print(f"  is_available() = {cold_item.is_available()}  ← Hardware Dependency Constraint enforced")


# ─── Scenario 4: Multiple Payment Providers ───────────────────────────────────

def scenario_4_payment_adapters():
    section("SCENARIO 4: Multiple Payment Providers (Adapter Pattern)")
    print("  Pattern demonstrated: Adapter – incompatible gateway APIs")
    print("  unified behind IPaymentProvider interface.")

    from payment.payment import TransactionStatus

    providers = [
        ("UPI",           UPIAdapter()),
        ("Credit Card",   CreditCardAdapter()),
        ("Digital Wallet", DigitalWalletAdapter()),
    ]

    for name, provider in providers:
        print(f"\n  ── Testing {name} provider")
        result = provider.process_payment(99.0, f"demo-purchase-{name}")
        print(f"  process_payment result: status={result['status'].value}, txn={result['transaction_id']}")
        refund = provider.refund(result["transaction_id"])
        print(f"  refund result: status={refund['status'].value}")

    print("\n  [Adapter] Same interface used for all three providers.")
    print("  Adding a new provider only requires a new Adapter class — no existing code changes.")


# ─── Scenario 5: Inventory Proxy Access Control ───────────────────────────────

def scenario_5_proxy_access():
    section("SCENARIO 5: Inventory Proxy – Access Control & Logging")
    print("  Pattern demonstrated: Proxy – authorization, logging,")
    print("  and access restrictions.")

    proxy = InventoryProxy()
    item  = Product("Paracetamol 500mg", price=50.0, stock=30,
                    requires_refrigeration=False)
    proxy.add_item(item, role="admin")

    print("\n  Testing different roles:")
    for role in ["admin", "kiosk", "auditor", "guest", "hacker"]:
        result = proxy.get_item("Paracetamol 500mg", role=role)
        found = result is not None
        print(f"  role={role!r:12} get_item → {'found' if found else 'DENIED/NOT FOUND'}")

    print("\n  Testing write access by role:")
    new_item = Product("Ibuprofen 400mg", price=60.0, stock=20)
    for role in ["admin", "kiosk", "auditor", "guest"]:
        success = proxy.add_item(new_item, role=role)
        print(f"  role={role!r:12} add_item → {'allowed' if success else 'DENIED'}")

    print(f"\n  Access log ({len(proxy.get_access_log())} entries):")
    for entry in proxy.get_access_log()[-5:]:  # show last 5
        print(f"    {entry}")


# ─── Main Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "█"*65)
    print("  AURA RETAIL OS – PATH B: MODULAR HARDWARE PLATFORM")
    print("  Subtask 2 Simulation | Group 24: Pixel Pioneers")
    print("█"*65)

    scenario_1_normal_purchase()
    scenario_2_hardware_replacement()
    scenario_3_dynamic_modules()
    scenario_4_payment_adapters()
    scenario_5_proxy_access()

    section("SIMULATION COMPLETE")
    print("  All Path B patterns demonstrated:")
    print("  ✓ Abstract Factory  – kiosk component families")
    print("  ✓ Bridge            – hardware abstraction + runtime replacement")
    print("  ✓ Decorator         – dynamic optional hardware modules")
    print("  ✓ Composite         – nested inventory items and bundles")
    print("  ✓ Proxy             – secured inventory access with logging")
    print("  ✓ Adapter           – unified payment provider interface")
    print("  ✓ Command           – atomic purchase/refund/restock operations")
    print("  ✓ Singleton         – CentralRegistry global config store")
    print("  ✓ Facade            – KioskInterface as single external entry point")
    print()
