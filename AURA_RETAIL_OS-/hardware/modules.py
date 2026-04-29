"""
hardware/modules.py
====================
DESIGN PATTERN: Decorator
--------------------------
Attaches optional hardware modules (Refrigeration, Solar Monitoring, Network)
to AuraKiosk dynamically at runtime without modifying the base kiosk class.

Decorator Structure:
  Component        -> HardwareModule (abstract base)
  ConcreteComponent -> BaseKioskHardware
  Decorators       -> RefrigerationModule, SolarMonitoringModule, NetworkModule
"""

from abc import ABC, abstractmethod


# --- Component Interface ---

class HardwareModule(ABC):
    """
    Decorator base. All hardware modules (base and decorators) implement this.
    """

    @abstractmethod
    def operate(self) -> str:
        """Run the module's primary operation."""
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """Return current status of this module and any wrapped modules."""
        pass

    @abstractmethod
    def get_module_name(self) -> str:
        pass


# --- Concrete Component ---

class BaseKioskHardware(HardwareModule):
    """
    The base hardware component that can be wrapped by decorators.
    Represents the core kiosk hardware with no optional modules.
    """

    def operate(self) -> str:
        return "BaseKioskHardware: core systems running."

    def get_status(self) -> dict:
        return {"base_hardware": "operational"}

    def get_module_name(self) -> str:
        return "BaseKioskHardware"


# --- Abstract Decorator ---

class HardwareModuleDecorator(HardwareModule, ABC):
    """
    Abstract decorator. Wraps a HardwareModule (component or another decorator).
    Forwards calls to the wrapped component and adds its own behavior.
    """

    def __init__(self, base_module: HardwareModule):
        self._base_module = base_module  # wrapped component

    def operate(self) -> str:
        return self._base_module.operate()

    def get_status(self) -> dict:
        return self._base_module.get_status()

    def get_module_name(self) -> str:
        return self._base_module.get_module_name()


# --- Concrete Decorators ---

class RefrigerationModule(HardwareModuleDecorator):
    """
    Decorator: Adds refrigeration capability.
    Required for perishable food/medicine products.
    Implements Hardware Dependency Constraint (products need refrigeration).
    """

    def __init__(self, base_module: HardwareModule, target_temp_celsius: float = 4.0):
        super().__init__(base_module)
        self._temperature = target_temp_celsius
        self._is_active = True
        self._current_temp = target_temp_celsius + 0.5  # simulated reading

    def operate(self) -> str:
        base_result = super().operate()
        return f"{base_result} | RefrigerationModule: maintaining {self._current_temp} deg C (target: {self._temperature} deg C)."

    def get_status(self) -> dict:
        status = super().get_status()
        status["refrigeration"] = {
            "active": self._is_active,
            "target_temp": self._temperature,
            "current_temp": self._current_temp,
        }
        return status

    def get_module_name(self) -> str:
        return super().get_module_name() + " + RefrigerationModule"

    def regulate(self, new_temp: float) -> None:
        self._temperature = new_temp
        print(f"  [RefrigerationModule] Target temperature updated to {new_temp} deg C")

    def is_active(self) -> bool:
        return self._is_active


class SolarMonitoringModule(HardwareModuleDecorator):
    """
    Decorator: Adds solar power monitoring capability.
    Tracks solar input and battery levels for off-grid kiosks.
    """

    def __init__(self, base_module: HardwareModule):
        super().__init__(base_module)
        self._solar_watts = 120.5   # simulated watt reading
        self._battery_pct = 87.0   # simulated battery %

    def operate(self) -> str:
        base_result = super().operate()
        return f"{base_result} | SolarMonitoringModule: {self._solar_watts}W input, battery {self._battery_pct}%."

    def get_status(self) -> dict:
        status = super().get_status()
        status["solar"] = {
            "solar_input_watts": self._solar_watts,
            "battery_percentage": self._battery_pct,
        }
        return status

    def get_module_name(self) -> str:
        return super().get_module_name() + " + SolarMonitoringModule"

    def get_battery_level(self) -> float:
        return self._battery_pct


class NetworkModule(HardwareModuleDecorator):
    """
    Decorator: Adds network connectivity monitoring.
    Required for payment processing and remote monitoring.
    """

    def __init__(self, base_module: HardwareModule, ssid: str = "AuraNet-5G"):
        super().__init__(base_module)
        self._ssid = ssid
        self._connected = True
        self._signal_strength = -52  # dBm

    def operate(self) -> str:
        base_result = super().operate()
        conn_str = f"connected to '{self._ssid}' ({self._signal_strength} dBm)" if self._connected else "DISCONNECTED"
        return f"{base_result} | NetworkModule: {conn_str}."

    def get_status(self) -> dict:
        status = super().get_status()
        status["network"] = {
            "connected": self._connected,
            "ssid": self._ssid,
            "signal_dbm": self._signal_strength,
        }
        return status

    def get_module_name(self) -> str:
        return super().get_module_name() + " + NetworkModule"

    def is_connected(self) -> bool:
        return self._connected

    def disconnect(self) -> None:
        self._connected = False
        print(f"  [NetworkModule] Disconnected from '{self._ssid}'")
