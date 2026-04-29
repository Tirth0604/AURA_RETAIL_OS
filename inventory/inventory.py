"""
inventory/inventory.py
=======================
DESIGN PATTERNS: Composite + Proxy
------------------------------------
Composite:
  IInventoryItem (interface) is implemented by both Product (leaf) and
  ProductBundle (composite). Bundles may nest other bundles; stock
  availability is computed recursively.

  Component  -> IInventoryItem
  Leaf       -> Product
  Composite  -> ProductBundle

Proxy:
  InventoryProxy wraps the real inventory catalogue with authorization
  checks, access control, and logging before every read/write.

  Subject    -> InventoryAccess (abstract)
  RealSubject -> InventoryCatalogue
  Proxy      -> InventoryProxy
"""

from abc import ABC, abstractmethod
from typing import List, Optional


# ─── Composite: Component Interface ──────────────────────────────────────────

class IInventoryItem(ABC):
    """
    Composite component interface.
    Both Product (leaf) and ProductBundle (composite node) implement this.
    """

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_price(self) -> float:
        """Compute item/bundle price."""
        pass

    @abstractmethod
    def get_stock(self) -> int:
        """Return available stock. For bundles: minimum across all children."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """True if the item can currently be purchased."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialise to dictionary for persistence."""
        pass


# ─── Composite: Leaf ─────────────────────────────────────────────────────────

class Product(IInventoryItem):
    """
    Composite Leaf. Represents a single physical product in the kiosk.
    Encapsulates price, stock, and hardware requirements.
    """

    def __init__(
        self,
        name: str,
        price: float,
        stock: int,
        requires_refrigeration: bool = False,
        refrigeration_available: bool = True,
    ):
        self._name = name
        self._price = price
        self._stock = stock
        self._requires_refrigeration = requires_refrigeration
        # Hardware Dependency Constraint (Path B §5.2.3)
        self._refrigeration_available = refrigeration_available

    # ── IInventoryItem implementation ──────────────────────────────────────

    def get_name(self) -> str:
        return self._name

    def get_price(self) -> float:
        return self._price

    def get_stock(self) -> int:
        return self._stock

    def is_available(self) -> bool:
        """
        Derived attribute: availability depends on stock AND hardware status.
        If product requires refrigeration but module is absent → unavailable.
        """
        if self._stock <= 0:
            return False
        if self._requires_refrigeration and not self._refrigeration_available:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "type": "Product",
            "name": self._name,
            "price": self._price,
            "stock": self._stock,
            "requires_refrigeration": self._requires_refrigeration,
        }

    # ── Encapsulated mutators ──────────────────────────────────────────────

    def reduce_stock(self, quantity: int = 1) -> bool:
        """Inventory Consistency Constraint: only called on successful transaction."""
        if self._stock >= quantity:
            self._stock -= quantity
            return True
        return False

    def restock(self, quantity: int) -> None:
        self._stock += quantity

    def set_refrigeration_available(self, available: bool) -> None:
        """Hardware Dependency Constraint: called when RefrigerationModule state changes."""
        self._refrigeration_available = available

    def __repr__(self) -> str:
<<<<<<< HEAD
        avail = "YES" if self.is_available() else "NO"
        return f"Product({self._name!r}, INR {self._price:.2f}, stock={self._stock}) [{avail}]"
=======
        avail = "✓" if self.is_available() else "✗"
        return f"Product({self._name!r}, ₹{self._price:.2f}, stock={self._stock}) [{avail}]"
>>>>>>> 1d63b70f812d10221d5c92df9cf3a89bfd7914f8


# ─── Composite: Composite Node ────────────────────────────────────────────────

class ProductBundle(IInventoryItem):
    """
    Composite Node. A bundle contains Products or other ProductBundles.
    Price = sum of all children's prices (with optional discount).
    Stock = min stock across all children (recursive).
    Nested bundles supported — Path B constraint §5.2.3.
    """

    def __init__(self, name: str, discount_pct: float = 0.0):
        self._name = name
        self._discount_pct = discount_pct  # e.g. 0.1 = 10% off bundle
        self._items: List[IInventoryItem] = []

    def add_item(self, item: IInventoryItem) -> None:
        self._items.append(item)
        print(f"  [ProductBundle '{self._name}'] Added item: {item.get_name()}")

    def remove_item(self, name: str) -> bool:
        before = len(self._items)
        self._items = [i for i in self._items if i.get_name() != name]
        return len(self._items) < before

    # ── IInventoryItem implementation ──────────────────────────────────────

    def get_name(self) -> str:
        return self._name

    def get_price(self) -> float:
        """Recursive: sum of all children, minus bundle discount."""
        total = sum(item.get_price() for item in self._items)
        return round(total * (1 - self._discount_pct), 2)

    def get_stock(self) -> int:
        """Recursive: minimum stock across all leaf products in the tree."""
        if not self._items:
            return 0
        return min(item.get_stock() for item in self._items)

    def is_available(self) -> bool:
        """Bundle available only if ALL children are available."""
        return all(item.is_available() for item in self._items)

    def to_dict(self) -> dict:
        return {
            "type": "ProductBundle",
            "name": self._name,
            "discount_pct": self._discount_pct,
            "items": [item.to_dict() for item in self._items],
        }

    def __repr__(self) -> str:
<<<<<<< HEAD
        avail = "YES" if self.is_available() else "NO"
        return (
            f"ProductBundle({self._name!r}, INR {self.get_price():.2f}, "
=======
        avail = "✓" if self.is_available() else "✗"
        return (
            f"ProductBundle({self._name!r}, ₹{self.get_price():.2f}, "
>>>>>>> 1d63b70f812d10221d5c92df9cf3a89bfd7914f8
            f"stock={self.get_stock()}, items={len(self._items)}) [{avail}]"
        )


# ─── Proxy: Subject Interface ─────────────────────────────────────────────────

class InventoryAccess(ABC):
    """Proxy subject interface. Both RealInventory and InventoryProxy implement this."""

    @abstractmethod
    def get_item(self, name: str) -> Optional[IInventoryItem]:
        pass

    @abstractmethod
    def add_item(self, item: IInventoryItem, role: str) -> bool:
        pass

    @abstractmethod
    def list_items(self, role: str) -> List[IInventoryItem]:
        pass

    @abstractmethod
    def update_stock(self, name: str, quantity_delta: int, role: str) -> bool:
        pass


# ─── Proxy: Real Subject ──────────────────────────────────────────────────────

class InventoryCatalogue(InventoryAccess):
    """
    Real inventory store. Contains the actual item catalogue.
    Should only be accessed through InventoryProxy.
    """

    def __init__(self):
        self._catalogue: dict[str, IInventoryItem] = {}

    def get_item(self, name: str) -> Optional[IInventoryItem]:
        return self._catalogue.get(name)

    def add_item(self, item: IInventoryItem, role: str = "system") -> bool:
        self._catalogue[item.get_name()] = item
        return True

    def list_items(self, role: str = "system") -> List[IInventoryItem]:
        return list(self._catalogue.values())

    def update_stock(self, name: str, quantity_delta: int, role: str = "system") -> bool:
        item = self._catalogue.get(name)
        if item and isinstance(item, Product):
            if quantity_delta < 0:
                return item.reduce_stock(abs(quantity_delta))
            else:
                item.restock(quantity_delta)
                return True
        return False


# ─── Proxy: Proxy ─────────────────────────────────────────────────────────────

class InventoryProxy(InventoryAccess):
    """
    DESIGN PATTERN: Proxy
    Wraps InventoryCatalogue with:
      - Authorization checks (role-based access)
      - Access logging
      - Access restriction (e.g., read-only for 'guest' role)

    External callers only ever touch InventoryProxy, never InventoryCatalogue directly.
    """

    # Roles and their allowed operations
    _PERMISSIONS = {
        "admin":   {"read", "write", "list"},
        "kiosk":   {"read", "write", "list"},
        "auditor": {"read", "list"},
        "guest":   {"read"},
    }

    def __init__(self):
        self._real_inventory = InventoryCatalogue()  # hidden real subject
        self._access_log: List[dict] = []

    def _log(self, role: str, operation: str, target: str, result: str) -> None:
        entry = {
            "role": role,
            "operation": operation,
            "target": target,
            "result": result,
        }
        self._access_log.append(entry)
<<<<<<< HEAD
        print(f"  [InventoryProxy LOG] role={role!r} op={operation!r} target={target!r} -> {result}")
=======
        print(f"  [InventoryProxy LOG] role={role!r} op={operation!r} target={target!r} → {result}")
>>>>>>> 1d63b70f812d10221d5c92df9cf3a89bfd7914f8

    def _authorize(self, role: str, operation: str) -> bool:
        allowed = self._PERMISSIONS.get(role, set())
        return operation in allowed

    # ── InventoryAccess implementation ────────────────────────────────────

    def get_item(self, name: str, role: str = "kiosk") -> Optional[IInventoryItem]:
        if not self._authorize(role, "read"):
            self._log(role, "get_item", name, "DENIED")
            return None
        item = self._real_inventory.get_item(name)
        result = "found" if item else "not_found"
        self._log(role, "get_item", name, result)
        return item

    def add_item(self, item: IInventoryItem, role: str = "admin") -> bool:
        if not self._authorize(role, "write"):
            self._log(role, "add_item", item.get_name(), "DENIED")
            return False
        success = self._real_inventory.add_item(item, role)
        self._log(role, "add_item", item.get_name(), "success" if success else "failed")
        return success

    def list_items(self, role: str = "kiosk") -> List[IInventoryItem]:
        if not self._authorize(role, "list"):
            self._log(role, "list_items", "*", "DENIED")
            return []
        items = self._real_inventory.list_items(role)
        self._log(role, "list_items", f"{len(items)} items", "success")
        return items

    def update_stock(self, name: str, quantity_delta: int, role: str = "kiosk") -> bool:
        if not self._authorize(role, "write"):
            self._log(role, "update_stock", name, "DENIED")
            return False
        success = self._real_inventory.update_stock(name, quantity_delta, role)
        self._log(role, "update_stock", name, "success" if success else "failed")
        return success

    def get_access_log(self) -> List[dict]:
        return list(self._access_log)
