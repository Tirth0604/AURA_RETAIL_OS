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
        self.cart = {}
        
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
        for key, label in [("hardware", "⚡ Hardware"), ("payment", "💳 Payments"), ("inventory", "🛒 Shop & Cart")]:
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

    # --- TAB 3: Shop & Cart ---
    def _build_scenario_3(self, parent):
        tk.Label(parent, text="Shop & Cart", font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Browse catalog, add items to cart, and process unified checkout.", font=FONTS["normal"], bg=COLORS["bg"], fg=COLORS["muted"]).pack(anchor="w", pady=(0, 25))

        container = tk.Frame(parent, bg=COLORS["bg"])
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3) # Catalog
        container.columnconfigure(1, weight=2) # Cart

        # --- Left Panel: Catalog ---
        self.catalog_frame = tk.Frame(container, bg=COLORS["card"], padx=20, pady=20)
        self.catalog_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        tk.Label(self.catalog_frame, text="Product Catalog", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        
        self.catalog_canvas = tk.Canvas(self.catalog_frame, bg=COLORS["card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.catalog_frame, orient="vertical", command=self.catalog_canvas.yview)
        self.catalog_inner = tk.Frame(self.catalog_canvas, bg=COLORS["card"])
        
        self.catalog_inner.bind("<Configure>", lambda e: self.catalog_canvas.configure(scrollregion=self.catalog_canvas.bbox("all")))
        self.catalog_canvas.create_window((0, 0), window=self.catalog_inner, anchor="nw", width=450)
        self.catalog_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.catalog_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- Right Panel: Cart & Checkout ---
        self.cart_frame = tk.Frame(container, bg=COLORS["card"], padx=20, pady=20)
        self.cart_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.cart_frame.pack_propagate(False)
        tk.Label(self.cart_frame, text="Your Cart", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["accent"]).pack(anchor="w", pady=(0, 10))
        
        # Cart Items Treeview
        tree_frame = tk.Frame(self.cart_frame, bg=COLORS["card"])
        tree_frame.pack(fill="both", expand=True)
        self.cart_tree = ttk.Treeview(tree_frame, columns=("Qty", "Price"), show="tree headings", height=6)
        self.cart_tree.heading("#0", text="Item")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Price", text="Total Price")
        self.cart_tree.column("#0", width=150)
        self.cart_tree.column("Qty", width=50, anchor="center")
        self.cart_tree.column("Price", width=80, anchor="center")
        self.cart_tree.pack(side="left", fill="both", expand=True)
        
        # Total Label
        self.cart_total_lbl = tk.Label(self.cart_frame, text="Total: ₹ 0.00", font=FONTS["header"], bg=COLORS["card"], fg=COLORS["text"])
        self.cart_total_lbl.pack(anchor="e", pady=(10, 10))
        
        # Checkout Actions
        btn_frame = tk.Frame(self.cart_frame, bg=COLORS["card"])
        btn_frame.pack(fill="x", pady=(0, 15))
        tk.Button(btn_frame, text="Clear Cart", font=FONTS["small"], bg=COLORS["sidebar"], fg=COLORS["danger"], bd=0, padx=10, pady=8, command=self._clear_cart).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        tk.Label(self.cart_frame, text="Payment Method", font=FONTS["small"], bg=COLORS["card"], fg=COLORS["muted"]).pack(anchor="w")
        self.cart_method = tk.StringVar(value="UPI")
        method_frame = tk.Frame(self.cart_frame, bg=COLORS["card"])
        method_frame.pack(fill="x", pady=(5, 15))
        for name in self.payment_providers.keys():
            tk.Radiobutton(method_frame, text=name, variable=self.cart_method, value=name, font=FONTS["small"], bg=COLORS["card"], fg=COLORS["text"], activebackground=COLORS["card"], activeforeground=COLORS["accent"], selectcolor=COLORS["sidebar"], bd=0, padx=5).pack(side="left")

        tk.Button(self.cart_frame, text="Checkout", font=FONTS["header"], bg=COLORS["accent"], fg=COLORS["bg"], bd=0, pady=12, command=self._checkout_cart).pack(fill="x")
        
        self.cart_status_lbl = tk.Label(self.cart_frame, text="Ready", font=FONTS["small"], bg=COLORS["card"], fg=COLORS["muted"], wraplength=250)
        self.cart_status_lbl.pack(pady=(15, 0))

        self._populate_catalog()
        self._refresh_cart_view()

    def _populate_catalog(self):
        for widget in self.catalog_inner.winfo_children():
            widget.destroy()
            
        items = self.facade.list_inventory()
        for i, obj in enumerate(items):
            frame = tk.Frame(self.catalog_inner, bg=COLORS["sidebar"], pady=10, padx=15)
            frame.pack(fill="x", pady=5)
            
            info_frame = tk.Frame(frame, bg=COLORS["sidebar"])
            info_frame.pack(side="left", fill="both", expand=True)
            
            tk.Label(info_frame, text=obj.get_name(), font=FONTS["header"], bg=COLORS["sidebar"], fg=COLORS["text"]).pack(anchor="w")
            tk.Label(info_frame, text=f"Price: ₹ {obj.get_price():.2f}  |  Stock: {obj.get_stock()}", font=FONTS["small"], bg=COLORS["sidebar"], fg=COLORS["muted"]).pack(anchor="w")
            
            req_fridge = getattr(obj, '_requires_refrigeration', False)
            if req_fridge:
                tk.Label(info_frame, text="Requires Refrigeration", font=("Segoe UI", 8), bg=COLORS["sidebar"], fg=COLORS["accent_dim"]).pack(anchor="w")
            
            avail = obj.is_available()
            btn_state = "normal" if avail else "disabled"
            btn_color = COLORS["accent"] if avail else COLORS["muted"]
            btn_text = "Add to Cart" if avail else "Unavailable"
            
            btn = tk.Button(frame, text=btn_text, font=FONTS["small"], bg=btn_color, fg=COLORS["bg"] if avail else COLORS["sidebar"], bd=0, padx=15, pady=8, state=btn_state, command=lambda o=obj: self._add_to_cart(o.get_name()))
            btn.pack(side="right", padx=(10, 0))

    def _add_to_cart(self, item_name):
        self.cart[item_name] = self.cart.get(item_name, 0) + 1
        self._refresh_cart_view()
        self.cart_status_lbl.config(text=f"Added {item_name} to cart.", fg=COLORS["success"])

    def _clear_cart(self):
        self.cart.clear()
        self._refresh_cart_view()
        self.cart_status_lbl.config(text="Cart cleared.", fg=COLORS["muted"])

    def _refresh_cart_view(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        total_price = 0.0
        for item_name, qty in self.cart.items():
            obj = self.proxy.get_item(item_name, role="admin")
            if obj:
                price = obj.get_price() * qty
                total_price += price
                self.cart_tree.insert("", "end", text=item_name, values=(qty, f"₹ {price:.2f}"))
                
        self.cart_total_lbl.config(text=f"Total: ₹ {total_price:.2f}")

    def _checkout_cart(self):
        if not self.cart:
            messagebox.showwarning("Cart Empty", "Add items to your cart before checking out.")
            return
            
        self.kiosk.payment = self.payment_providers[self.cart_method.get()]
        success = self.facade.purchase_cart(self.cart)
        
        if success:
            messagebox.showinfo("Checkout Complete", "Purchase successful! Items dispensed.")
            self.cart.clear()
            self._refresh_cart_view()
            self._populate_catalog()
            self.cart_status_lbl.config(text="Checkout successful.", fg=COLORS["success"])
        else:
            messagebox.showerror("Checkout Failed", "Transaction failed or cancelled. Payment rolled back.")
            self.cart_status_lbl.config(text="Checkout failed.", fg=COLORS["danger"])
            self._populate_catalog()

if __name__ == "__main__":
    app = AuraRetailGUI()
    app.mainloop()
