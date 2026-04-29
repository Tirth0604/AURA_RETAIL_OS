"""
hardware/dispenser.py
======================
DESIGN PATTERN: Bridge
-----------------------
Separates the high-level Dispenser abstraction from concrete hardware
implementations. The abstraction (Dispenser) holds a reference to an
IDispenser implementor. Hardware can be swapped at runtime without
changing business logic.

Bridge Structure:
  Abstraction  -> Dispenser (holds reference to IDispenser)
  Implementor  -> IDispenser (interface)
  Concrete Impl -> SpiralDispenser, RoboticArmDispenser, ConveyorDispenser
"""

from abc import ABC, abstractmethod


# ─── Implementor Interface ────────────────────────────────────────────────────

class IDispenser(ABC):
    """Bridge implementor interface. All hardware dispensers must implement this."""

    @abstractmethod
    def dispense(self, item: str) -> bool:
        """Physically dispense the item. Returns True on success."""
        pass

    @abstractmethod
    def retract(self, item: str) -> bool:
        """Retract a dispensed item (used during rollback). Returns True on success."""
        pass

    @abstractmethod
    def calibrate(self) -> bool:
        """Calibrate hardware. Returns True if calibration succeeds."""
        pass

    @abstractmethod
    def get_hardware_name(self) -> str:
        """Return human-readable hardware name."""
        pass


# ─── Concrete Implementors ────────────────────────────────────────────────────

class SpiralDispenser(IDispenser):
    """
    Concrete Implementor – Spiral motor-based item dispenser.
    Typically used in snack/beverage kiosks.
    """

    def __init__(self, motor_id: int):
        self._motor_id = motor_id  # Encapsulated hardware attribute

    def dispense(self, item: str) -> bool:
        print(f"  [SpiralDispenser | Motor #{self._motor_id}] Rotating spiral to dispense '{item}'...")
        return True

    def retract(self, item: str) -> bool:
        print(f"  [SpiralDispenser | Motor #{self._motor_id}] Reversing spiral to retract '{item}'...")
        return True

    def calibrate(self) -> bool:
        print(f"  [SpiralDispenser | Motor #{self._motor_id}] Running calibration cycle...")
        return True

    def get_hardware_name(self) -> str:
        return f"SpiralDispenser(motor_id={self._motor_id})"


class RoboticArmDispenser(IDispenser):
    """
    Concrete Implementor – Robotic arm dispenser.
    Used in pharmacy kiosks for precise medicine dispensing.
    """

    def __init__(self, arm_id: str):
        self._arm_id = arm_id

    def dispense(self, item: str) -> bool:
        print(f"  [RoboticArmDispenser | Arm '{self._arm_id}'] Extending arm to pick and place '{item}'...")
        return True

    def retract(self, item: str) -> bool:
        print(f"  [RoboticArmDispenser | Arm '{self._arm_id}'] Arm retracting '{item}' to tray...")
        return True

    def calibrate(self) -> bool:
        print(f"  [RoboticArmDispenser | Arm '{self._arm_id}'] Performing arm calibration sequence...")
        return True

    def get_hardware_name(self) -> str:
        return f"RoboticArmDispenser(arm_id={self._arm_id})"


class ConveyorDispenser(IDispenser):
    """
    Concrete Implementor – Conveyor belt dispenser.
    Used in food kiosks and emergency supply distribution.
    """

    def __init__(self, belt_speed: float = 1.0):
        self._belt_speed = belt_speed  # speed in m/s

    def dispense(self, item: str) -> bool:
        print(f"  [ConveyorDispenser | Speed {self._belt_speed}m/s] Moving belt to deliver '{item}'...")
        return True

    def retract(self, item: str) -> bool:
        print(f"  [ConveyorDispenser | Speed {self._belt_speed}m/s] Reversing belt to retract '{item}'...")
        return True

    def calibrate(self) -> bool:
        print(f"  [ConveyorDispenser | Speed {self._belt_speed}m/s] Calibrating belt speed and alignment...")
        return True

    def get_hardware_name(self) -> str:
        return f"ConveyorDispenser(belt_speed={self._belt_speed})"


# ─── Abstraction ──────────────────────────────────────────────────────────────

class Dispenser:
    """
    Bridge Abstraction. Works with any IDispenser implementor.
    Business logic calls this class; hardware details are hidden.
    Supports runtime hardware replacement (Path B constraint).
    """

    def __init__(self, hardware: IDispenser):
        self._hardware = hardware  # Bridge reference to implementor

    def replace_hardware(self, new_hardware: IDispenser) -> None:
        """
        Runtime hardware replacement – Path B constraint.
        Swaps the underlying implementor without restarting the system.
        """
        old_name = self._hardware.get_hardware_name()
        self._hardware = new_hardware
        print(f"  [Dispenser] Hardware replaced: {old_name} -> {new_hardware.get_hardware_name()}")

    def dispense_item(self, item: str) -> bool:
        """High-level dispense operation delegated to hardware implementor."""
        print(f"  [Dispenser] Requesting dispense of '{item}'")
        return self._hardware.dispense(item)

    def retract_item(self, item: str) -> bool:
        """High-level retract operation delegated to hardware implementor."""
        print(f"  [Dispenser] Requesting retract of '{item}'")
        return self._hardware.retract(item)

    def run_calibration(self) -> bool:
        """Trigger hardware calibration through abstraction layer."""
        print(f"  [Dispenser] Starting calibration on {self._hardware.get_hardware_name()}")
        return self._hardware.calibrate()

    def get_status(self) -> dict:
        return {"hardware": self._hardware.get_hardware_name(), "status": "operational"}
