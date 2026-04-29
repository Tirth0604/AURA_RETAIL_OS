import os
import sys
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.kiosk import CentralRegistry, AuraKiosk, KioskInterface
from hardware.dispenser import Dispenser, SpiralDispenser
from hardware.modules import NetworkModule, RefrigerationModule, SolarMonitoringModule
from inventory.inventory import InventoryProxy, Product, ProductBundle
from payment.payment import UPIAdapter, CreditCardAdapter, DigitalWalletAdapter, TransactionStatus

app = FastAPI(title="Aura Retail OS - Web API")

# Initialize System
registry = CentralRegistry()
registry.initialize()

dispenser = Dispenser(SpiralDispenser(motor_id=1))
proxy = InventoryProxy()

# Add initial stock
water = Product("Water Bottle", price=15.0, stock=50)
chips = Product("Lays Chips", price=20.0, stock=40)
kit = Product("First Aid Kit", price=150.0, stock=15)
insulin = Product("Insulin Pen", price=450.0, stock=10, requires_refrigeration=True, refrigeration_available=True)

survival_bundle = ProductBundle("Survival Kit", discount_pct=0.10)
survival_bundle.add_item(water)
survival_bundle.add_item(chips)
survival_bundle.add_item(kit)

proxy.add_item(water, role="admin")
proxy.add_item(chips, role="admin")
proxy.add_item(kit, role="admin")
proxy.add_item(insulin, role="admin")
proxy.add_item(survival_bundle, role="admin")

payment_providers = {
    "UPI": UPIAdapter(),
    "Card": CreditCardAdapter(),
    "Wallet": DigitalWalletAdapter()
}

# Start with UPI as default
kiosk = AuraKiosk("AURA-WEB-01", dispenser, proxy, payment_providers["UPI"])
facade = KioskInterface(kiosk)

# --- API Models ---
class PurchaseRequest(BaseModel):
    item_name: str
    quantity: int

class PaymentMethodRequest(BaseModel):
    method: str

class ChargeRequest(BaseModel):
    amount: float
    description: str

# --- API Endpoints ---

@app.get("/api/status")
def get_status():
    return facade.run_diagnostics()

@app.get("/api/inventory")
def get_inventory():
    items = facade.list_inventory()
    result = []
    for obj in items:
        result.append({
            "name": obj.get_name(),
            "price": obj.get_price(),
            "stock": obj.get_stock(),
            "requires_refrigeration": getattr(obj, '_requires_refrigeration', False),
            "available": obj.is_available()
        })
    return result

@app.post("/api/purchase")
def purchase_item(req: PurchaseRequest):
    success = facade.purchase_item(req.item_name, req.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Purchase failed (Check stock or requirements)")
    return {"status": "success", "message": f"Purchased {req.quantity} {req.item_name}"}

@app.post("/api/payment/method")
def set_payment_method(req: PaymentMethodRequest):
    if req.method not in payment_providers:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    kiosk.payment = payment_providers[req.method]
    return {"status": "success", "method": req.method}

@app.post("/api/payment/charge")
def process_payment(req: ChargeRequest):
    res = kiosk.payment.process_payment(req.amount, req.description)
    success = res.get("status") == TransactionStatus.SUCCESS
    return {
        "status": "success" if success else "failed",
        "transaction_id": res.get("transaction_id", "N/A"),
        "amount": req.amount
    }

@app.post("/api/hardware/module/{mod_type}")
def add_module(mod_type: str):
    if mod_type == "network":
        kiosk.add_module(NetworkModule, ssid="AuraNet-Web")
    elif mod_type == "fridge":
        kiosk.add_module(RefrigerationModule, target_temp_celsius=4.0)
    elif mod_type == "solar":
        kiosk.add_module(SolarMonitoringModule)
    else:
        raise HTTPException(status_code=400, detail="Unknown module type")
    return {"status": "success", "message": f"{mod_type.title()} module added"}

@app.delete("/api/hardware/module/{mod_type}")
def remove_module_api(mod_type: str):
    facade.remove_hardware_module(mod_type)
    return {"status": "success", "message": f"{mod_type.title()} module removed"}

@app.post("/api/return")
def return_item(req: PurchaseRequest):
    success = facade.restock_inventory(req.item_name, req.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Return failed")
    return {"status": "success", "message": f"Returned {req.quantity} {req.item_name} to stock"}

# Serve Frontend
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
