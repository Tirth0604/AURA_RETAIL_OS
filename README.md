# 🛒 Aura Retail OS — Path B: Modular Hardware Platform

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Modular-green)
![Design Patterns](https://img.shields.io/badge/Design%20Patterns-9%2F9-orange)

## 📋 Overview
Aura Retail OS is a next-generation autonomous kiosk system designed for Smart-City infrastructure. This repository implements **Path B: Modular Hardware Platform**, focusing on a highly decoupled hardware abstraction layer that supports runtime hot-swapping and dynamic capability extension.

This implementation satisfies all requirements for **IT620 Project Subtask 2**.

---

## 🛠️ Key Design Patterns (9/9)
| Pattern | Implementation Role |
| :--- | :--- |
| **Abstract Factory** | Orchestrates families of compatible components (Pharmacy, Food, Emergency). |
| **Singleton** | CentralRegistry for synchronized global system configuration. |
| **Facade** | KioskInterface provides a simplified API for external users and subsystems. |
| **Bridge** | Decouples Dispenser logic from hardware (Spiral, Robotic Arm, Conveyor). |
| **Composite** | Models complex hierarchical inventory and recursive product bundles. |
| **Proxy** | Enforces Role-Based Access Control (RBAC) and captures audit logs. |
| **Decorator** | Dynamically attaches capabilities (Refrigeration, Solar, Network) at runtime. |
| **Adapter** | Unifies UPI, Credit Card, and Digital Wallet gateways under one interface. |
| **Command** | Ensures atomic transactions (Payment → Dispense → Stock Update) with Rollback. |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher.
- `tkinter` library (standard with most Python installations).

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Tirth0604/AURA_RETAIL_OS.git
   cd AURA_RETAIL_OS
   ```

### Running the Dashboard (Recommended for Demos)
The project includes a professional **Intelligence Dashboard** that tracks design pattern compliance in real-time.

```bash
python gui.py
```
1. Click **"LAUNCH SYSTEM AUDIT"**.
2. Watch the **Pattern Tracker** on the left light up as the system verifies each design requirement.

### Running via Terminal
To see the raw engineering logs:
```bash
python simulation/simulation.py
```

---

## 📂 Project Structure
```text
aura_retail_os/
├── core/             # Facade, Command, Singleton
├── hardware/         # Bridge, Decorator, Abstract Factory
├── inventory/        # Composite, Proxy
├── payment/          # Adapter (UPI, CC, Wallet)
├── persistence/      # JSON/CSV Persistence layer
├── simulation/       # 5 demonstration scenarios
├── gui.py            # Interactive Intelligence Dashboard
└── README.md         # Documentation
```

---

## 👥 Authors (Group 24: Pixel Pioneers)
- **Heer Shah** [202512024] - Core Architecture & Facade
- **Diya Shah** [202512025] - Inventory System & Proxy
- **Tirth Gandhi** [202512038] - Payment System & Adapters
- **Nishit Gal** [202512002] - Hardware Abstraction & Factories
