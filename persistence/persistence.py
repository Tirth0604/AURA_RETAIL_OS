"""
persistence/persistence.py
===========================
Handles loading and saving of:
  - inventory.json   (product catalogue)
  - config.json      (kiosk configuration)
  - transactions.csv (appended per transaction by payment module)
"""

import json
import os
from inventory.inventory import InventoryProxy, Product, ProductBundle


def load_inventory(proxy: InventoryProxy, filepath: str = "inventory.json") -> None:
    """Load products from inventory.json into the InventoryProxy."""
    if not os.path.exists(filepath):
        print(f"  [Persistence] '{filepath}' not found. Starting with empty inventory.")
        return

    with open(filepath) as f:
        data = json.load(f)

    for entry in data.get("items", []):
        if entry["type"] == "Product":
            product = Product(
                name=entry["name"],
                price=entry["price"],
                stock=entry["stock"],
                requires_refrigeration=entry.get("requires_refrigeration", False),
            )
            proxy.add_item(product, role="admin")
        # Bundles would be reconstructed here in a full implementation

    print(f"  [Persistence] Loaded {len(data.get('items', []))} items from '{filepath}'.")


def save_inventory(proxy: InventoryProxy, filepath: str = "inventory.json") -> None:
    """Persist current inventory to inventory.json."""
    items = proxy.list_items(role="admin")
    data = {"items": [item.to_dict() for item in items]}
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [Persistence] Saved {len(items)} items to '{filepath}'.")


def load_config(filepath: str = "config.json") -> dict:
    """Load kiosk config from JSON file."""
    if not os.path.exists(filepath):
        config = {
            "kiosk_id": "AURA-001",
            "mode": "active",
            "emergency_purchase_limit": 2,
            "version": "2.0-subtask2",
        }
        save_config(config, filepath)
        return config
    with open(filepath) as f:
        return json.load(f)


def save_config(config: dict, filepath: str = "config.json") -> None:
    """Save config to JSON file."""
    with open(filepath, "w") as f:
        json.dump(config, f, indent=2)
