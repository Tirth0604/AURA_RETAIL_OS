import tkinter as tk
from tkinter import ttk, messagebox
import json

from core.kiosk import CentralRegistry, AuraKiosk, KioskInterface
from hardware.dispenser import Dispenser, SpiralDispenser
from hardware.modules import NetworkModule, RefrigerationModule, SolarMonitoringModule
from inventory.inventory import InventoryProxy, Product, ProductBundle
from payment.payment import UPIAdapter, CreditCardAdapter, DigitalWalletAdapter

# --- Colors and Styles ---
COLORS = {
    "bg": "#F4F7F6",          
    "sidebar": "#E8ECEB",     
    "card": "#FFFFFF",        
    "accent": "#5B8FB9",      
    "accent_dim": "#B6E2D3",  
    "text": "#2B3A42",        
    "muted": "#7A8B99",       
    "success": "#44A08D",     
    "danger": "#D96C6C",      
}

FONTS = {
    "title": ("Segoe UI Semibold", 22),
    "header": ("Segoe UI Bold", 13),
    "normal": ("Segoe UI", 10),
    "mono": ("Consolas", 10),
    "small": ("Segoe UI", 9)
}

class AuraRetailGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aura Retail OS")
        self.geometry("1100x720")
        self.configure(bg=COLORS["bg"])

        self._init_system()
        self._init_styles()
        self._build_layout()
        self._switch_page("hardware")

    def _init_system(self):
        self.registry = CentralRegistry()
        self.registry.initialize()
        
        self.dispenser = Dispenser(SpiralDispenser(motor_id=1))
        self.proxy = InventoryProxy()
        
        self.water = Product("Water Bottle", price=15.0, stock=50)
        self.chips = Product("Lays Chips", price=20.0, stock=40)
        self.kit = Product("First Aid Kit", price=150.0, stock=15)
        self.insulin = Product("Insulin Pen", price=450.0, stock=10, requires_refrigeration=True, refrigeration_available=True)
        
        self.survival_bundle = ProductBundle("Survival Kit", discount_pct=0.10)
        self.survival_bundle.add_item(self.water)
        self.survival_bundle.add_item(self.chips)
        self.survival_bundle.add_item(self.kit)
        
        self.proxy.add_item(self.water, role="admin")
        self.proxy.add_item(self.chips, role="admin")
        self.proxy.add_item(self.kit, role="admin")
        self.proxy.add_item(self.insulin, role="admin")
        self.proxy.add_item(self.survival_bundle, role="admin")
        
        self.payment_providers = {
            "UPI": UPIAdapter(),
            "Card": CreditCardAdapter(),
            "Wallet": DigitalWalletAdapter()
        }
        
        # Start with UPI
        self.kiosk = AuraKiosk("AURA-GUI-01", self.dispenser, self.proxy, self.payment_providers["UPI"])
        self.facade = KioskInterface(self.kiosk)
        
    def _init_styles(self):
        s = ttk.Style(self)
        try: s.theme_use("clam")
        except: pass
        s.configure("TFrame", background=COLORS["bg"])
        s.configure("Sidebar.TFrame", background=COLORS["sidebar"])
        s.configure("Card.TFrame", background=COLORS["card"])
        s.configure("Treeview", background=COLORS["card"], foreground=COLORS["text"], fieldbackground=COLORS["card"], borderwidth=0, font=FONTS["small"])
        s.configure("Treeview.Heading", background=COLORS["sidebar"], foreground=COLORS["accent"], font=FONTS["small"], borderwidth=0)
        s.map("Treeview", background=[("selected", COLORS["accent_dim"])])

    def _build_layout(self):
        # Sidebar
        self.sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=30)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="AURA", font=("Segoe UI Bold", 28), bg=COLORS["sidebar"], fg=COLORS["accent"]).pack()
        tk.Label(logo_frame, text="RETAIL OS", font=("Segoe UI", 10, "bold"), bg=COLORS["sidebar"], fg=COLORS["muted"], padx=5).pack()

        nav_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar"], pady=20)
        nav_frame.pack(fill="both", expand=True)

        self.nav_buttons = {}
        for key, label in [("hardware", "⚡ Hardware"), ("payment", "💳 Payments"), ("inventory", "📦 Inventory")]:
            btn = tk.Button(nav_frame, text=label, font=FONTS["header"], bg=COLORS["sidebar"], fg=COLORS["muted"], activebackground=COLORS["card"], activeforeground=COLORS["accent"], bd=0, padx=20, pady=12, anchor="w", command=lambda k=key: self._switch_page(k))
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        self.main_container = ttk.Frame(self)
        self.main_container.pack(side="right", fill="both", expand=True, padx=40, pady=30)

        self.pages = {}
        for key in ["hardware", "payment", "inventory"]:
            self.pages[key] = ttk.Frame(self.main_container)
        
        self._build_scenario_1(self.pages["hardware"])
        self._build_scenario_2(self.pages["payment"])
        self._build_scenario_3(self.pages["inventory"])

    def _switch_page(self, key):
        for p in self.pages.values(): p.pack_forget()
        self.pages[key].pack(fill="both", expand=True)
        for k, btn in self.nav_buttons.items():
            btn.config(fg=COLORS["accent"] if k == key else COLORS["muted"], bg=COLORS["card"] if k == key else COLORS["sidebar"])

    # --- TAB 1: Hardware ---
    def _build_scenario_1(self, parent):
        tk.Label(parent, text="Hardware Modules", font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Connect and manage modular components via Decorator.", font=FONTS["normal"], bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(0, 25))

        container = tk.Frame(parent, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1); container.columnconfigure(1, weight=1)

        lp = tk.Frame(container, bg=COLORS["card"], padx=20, pady=20)
        lp.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(lp, text="Registration", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 15))
        
        btn_opts = {"font": FONTS["normal"], "bg": COLORS["sidebar"], "fg": COLORS["text"], "activebackground": COLORS["accent"], "bd": 0, "pady": 8}
        tk.Button(lp, text="+ Network Module", **btn_opts, command=lambda: self._s1_add_module("network")).pack(fill="x", pady=4)
        tk.Button(lp, text="+ Refrigeration Module", **btn_opts, command=lambda: self._s1_add_module("fridge")).pack(fill="x", pady=4)
        tk.Button(lp, text="+ Solar Module", **btn_opts, command=lambda: self._s1_add_module("solar")).pack(fill="x", pady=4)
        tk.Button(lp, text="Run Diagnostics", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["success"], bd=0, pady=8, command=self._s1_diagnostics).pack(fill="x", pady=(15,0))

        rp = tk.Frame(container, bg=COLORS["card"], padx=20, pady=20)
        rp.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(rp, text="Hardware Dashboard", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        
        tree_frame = tk.Frame(rp, bg=COLORS["card"])
        tree_frame.pack(fill="both", expand=True)
        self.s1_tree = ttk.Treeview(tree_frame, columns=("Status"), show="tree headings")
        self.s1_tree.heading("#0", text="Component")
        self.s1_tree.heading("Status", text="Status")
        self.s1_tree.column("#0", width=250)
        self.s1_tree.column("Status", width=150, anchor="center")
        self.s1_tree.pack(side="left", fill="both", expand=True)
        self._s1_refresh_table()

    def _s1_add_module(self, mod_type):
        if mod_type == "network": self.kiosk.add_module(NetworkModule, ssid="AuraNet-5G")
        elif mod_type == "fridge": self.kiosk.add_module(RefrigerationModule, target_temp_celsius=4.0)
        elif mod_type == "solar": self.kiosk.add_module(SolarMonitoringModule)
        self._s1_refresh_table()
        messagebox.showinfo("Hardware", "Module successfully added to the kiosk stack.")

    def _s1_refresh_table(self):
        for item in self.s1_tree.get_children(): self.s1_tree.delete(item)
        status = self.facade.run_diagnostics()
        
        disp_stat = status.get("dispenser", {})
        self.s1_tree.insert("", "end", text=disp_stat.get("hardware", "Dispenser"), values=(disp_stat.get("status", "Unknown"),))
        
        hw_mods = status.get("hardware_modules", {})
        if hw_mods.get("base_hardware"):
            self.s1_tree.insert("", "end", text="Base Hardware", values=(hw_mods["base_hardware"].title(),))
            
        if "network" in hw_mods:
            net = hw_mods["network"]
            stat = "Connected" if net.get("connected") else "Disconnected"
            self.s1_tree.insert("", "end", text="Network Module", values=(f"{stat} ({net.get('ssid')})",))
            
        if "refrigeration" in hw_mods:
            ref = hw_mods["refrigeration"]
            stat = "Active" if ref.get("active") else "Inactive"
            self.s1_tree.insert("", "end", text="Refrigeration Module", values=(f"{stat} ({ref.get('current_temp')}°C)",))
            
        if "solar" in hw_mods:
            sol = hw_mods["solar"]
            self.s1_tree.insert("", "end", text="Solar Module", values=(f"{sol.get('battery_percentage')}% Battery",))

    def _s1_diagnostics(self):
        self._s1_refresh_table()
        messagebox.showinfo("Diagnostics", "Diagnostics completed. See dashboard for details.")

    # --- TAB 2: Payment ---
    def _build_scenario_2(self, parent):
        tk.Label(parent, text="Payment Gateway", font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Interchangeable payment providers via Adapter pattern.", font=FONTS["normal"], bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(0, 25))

        container = tk.Frame(parent, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1); container.columnconfigure(1, weight=1)

        lp = tk.Frame(container, bg=COLORS["card"], padx=25, pady=25)
        lp.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(lp, text="Checkout", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 15))
        
        self.s2_method = tk.StringVar(value="UPI")
        for name in self.payment_providers.keys():
            tk.Radiobutton(lp, text=name, variable=self.s2_method, value=name, font=FONTS["normal"], bg=COLORS["card"], fg=COLORS["text"], activebackground=COLORS["card"], activeforeground=COLORS["accent"], selectcolor=COLORS["sidebar"], bd=0, padx=10, pady=5, command=self._s2_change_method).pack(anchor="w")

        tk.Frame(lp, bg=COLORS["bg"], height=1).pack(fill="x", pady=20)
        tk.Label(lp, text="Amount (INR)", font=FONTS["small"], bg=COLORS["card"], fg=COLORS["muted"]).pack(anchor="w")
        self.s2_amount = tk.Entry(lp, font=FONTS["header"], bg=COLORS["sidebar"], fg=COLORS["text"], insertbackground=COLORS["accent"], bd=0, highlightthickness=1)
        self.s2_amount.insert(0, "100.00")
        self.s2_amount.pack(fill="x", pady=(5, 20), ipady=8)
        tk.Button(lp, text="Complete Transaction", font=FONTS["header"], bg=COLORS["accent"], fg=COLORS["bg"], bd=0, pady=12, command=self._s2_charge).pack(fill="x")

        rp = tk.Frame(container, bg=COLORS["card"], padx=20, pady=20)
        rp.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        tk.Label(rp, text="Transaction Status", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["muted"]).pack(anchor="w", pady=(0, 10))
        
        receipt_frame = tk.Frame(rp, bg=COLORS["sidebar"], padx=20, pady=20)
        receipt_frame.pack(fill="both", expand=True)
        self.s2_status_lbl = tk.Label(receipt_frame, text="Awaiting Transaction...", font=FONTS["header"], bg=COLORS["sidebar"], fg=COLORS["muted"])
        self.s2_status_lbl.pack(pady=(20, 10))
        
        details_frame = tk.Frame(receipt_frame, bg=COLORS["sidebar"])
        details_frame.pack(fill="x", pady=10)
        tk.Label(details_frame, text="Amount:", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["muted"]).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.s2_rec_amount = tk.Label(details_frame, text="-", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["text"])
        self.s2_rec_amount.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(details_frame, text="Method:", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["muted"]).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.s2_rec_method = tk.Label(details_frame, text="-", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["text"])
        self.s2_rec_method.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(details_frame, text="TXN ID:", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["muted"]).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.s2_rec_txnid = tk.Label(details_frame, text="-", font=FONTS["mono"], bg=COLORS["sidebar"], fg=COLORS["text"])
        self.s2_rec_txnid.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        rf = tk.Frame(rp, bg=COLORS["sidebar"], pady=10, padx=10)
        rf.pack(fill="x", side="bottom", pady=(10, 0))
        self.s2_txn = tk.Entry(rf, font=FONTS["small"], bg=COLORS["card"], fg=COLORS["muted"], bd=0)
        self.s2_txn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Button(rf, text="Refund", font=FONTS["small"], bg=COLORS["danger"], fg=COLORS["text"], bd=0, padx=10, command=self._s2_refund).pack(side="right")

    def _s2_change_method(self):
        method = self.s2_method.get()
        self.kiosk.payment = self.payment_providers[method]

    def _s2_charge(self):
        method = self.s2_method.get()
        try: amount = float(self.s2_amount.get())
        except ValueError: messagebox.showerror("Error", "Invalid amount"); return
        
        res = self.kiosk.payment.process_payment(amount, "GUI-Charge")
        from payment.payment import TransactionStatus
        success = res.get("status") == TransactionStatus.SUCCESS
        txn_id = res.get("transaction_id", "")
        
        self.s2_status_lbl.config(text="Payment Successful" if success else "Payment Failed", fg=COLORS["success"] if success else COLORS["danger"])
        self.s2_rec_amount.config(text=f"₹ {amount:.2f}")
        self.s2_rec_method.config(text=method)
        self.s2_rec_txnid.config(text=txn_id if txn_id else "N/A")
        
        if success:
            self.s2_txn.delete(0, tk.END)
            self.s2_txn.insert(0, txn_id)

    def _s2_refund(self):
        method = self.s2_method.get()
        txn_id = self.s2_txn.get()
        if not txn_id: messagebox.showwarning("Warning", "Enter a transaction ID"); return
        
        ok = self.facade.refund_transaction(txn_id)
        self.s2_status_lbl.config(text="Refund Successful" if ok else "Refund Failed", fg=COLORS["success"] if ok else COLORS["danger"])
        self.s2_rec_method.config(text=method)
        self.s2_rec_txnid.config(text=txn_id)

    # --- TAB 3: Inventory ---
    def _build_scenario_3(self, parent):
        tk.Label(parent, text="Inventory & Bundles", font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Composite product bundles and hardware-dependent availability.", font=FONTS["normal"], bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(0, 25))

        container = tk.Frame(parent, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1); container.columnconfigure(1, weight=0)

        lp = tk.Frame(container, bg=COLORS["card"], padx=20, pady=20)
        lp.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(lp, text="System Stock", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        
        tree_frame = tk.Frame(lp, bg=COLORS["card"])
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=("Price", "Qty", "Req", "Avail"), show="tree headings", height=12)
        self.tree.heading("#0", text="Item")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Qty", text="Stock")
        self.tree.heading("Req", text="H/W Req")
        self.tree.heading("Avail", text="Status")
        self.tree.column("#0", width=220)
        self.tree.column("Price", width=80, anchor="center")
        self.tree.column("Qty", width=80, anchor="center")
        self.tree.column("Req", width=100, anchor="center")
        self.tree.column("Avail", width=80, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        self._populate_tree()

        rp = tk.Frame(container, bg=COLORS["card"], padx=20, pady=20, width=300)
        rp.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        rp.pack_propagate(False)
        tk.Label(rp, text="Control Center", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 15))
        
        tk.Button(rp, text="Simulate Purchase (Water)", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["accent"], bd=0, pady=10, command=self._s3_purchase).pack(fill="x", pady=4)
        tk.Button(rp, text="Quick Restock (Water)", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["muted"], bd=0, pady=10, command=self._s3_restock).pack(fill="x", pady=4)
        tk.Button(rp, text="Refresh Inventory", font=FONTS["normal"], bg=COLORS["card"], fg=COLORS["muted"], bd=0, pady=10, command=self._populate_tree).pack(fill="x", pady=(20, 0))

        tk.Label(rp, text="Recent Activity", font=FONTS["small"], bg=COLORS["card"], fg=COLORS["muted"]).pack(anchor="w", pady=(20, 5))
        self.s3_status_frame = tk.Frame(rp, bg=COLORS["sidebar"], pady=15, padx=15)
        self.s3_status_frame.pack(fill="x")
        self.s3_status_lbl = tk.Label(self.s3_status_frame, text="Ready", font=FONTS["normal"], bg=COLORS["sidebar"], fg=COLORS["success"], wraplength=250)
        self.s3_status_lbl.pack(fill="both")

    def _s3_set_status(self, msg, success=True):
        self.s3_status_lbl.config(text=msg, fg=COLORS["success"] if success else COLORS["danger"])

    def _populate_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        items = self.facade.list_inventory()
        for obj in items:
            req = "Yes" if getattr(obj, '_requires_refrigeration', False) else "-"
            self.tree.insert("", "end", text=obj.get_name(), values=(f"{obj.get_price():.2f}", obj.get_stock(), req, str(obj.is_available())))

    def _s3_purchase(self):
        success = self.facade.purchase_item("Water Bottle", 1)
        self._s3_set_status("Purchase successful!" if success else "Purchase failed.", success=success)
        if success: messagebox.showinfo("Purchase Complete", "Water Bottle purchased.")
        else: messagebox.showerror("Purchase Failed", "Could not purchase Water Bottle.")
        self._populate_tree()

    def _s3_restock(self):
        success = self.facade.restock_inventory("Water Bottle", 10)
        self._s3_set_status("Restock successful!" if success else "Restock failed.", success=success)
        if success: messagebox.showinfo("Restock Complete", "Added 10 Water Bottles.")
        self._populate_tree()

if __name__ == "__main__":
    app = AuraRetailGUI()
    app.mainloop()
