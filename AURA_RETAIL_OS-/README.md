# 🛒 Aura Retail OS — Path B: Modular Hardware Platform

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![Architecture](https://img.shields.io/badge/Architecture-Modular-green)
![Design Patterns](https://img.shields.io/badge/Design%20Patterns-9%2F9-orange)

## 📋 Overview
Aura Retail OS is a next-generation autonomous kiosk system designed for Smart-City infrastructure. This repository implements **Path B: Modular Hardware Platform**, focusing on a highly decoupled hardware abstraction layer that supports runtime hot-swapping and dynamic capability extension.

This implementation satisfies all requirements for **IT620 Project Subtask 2**.

---

## 🚀 Getting Started

### 1. Prerequisites
Before running the system, ensure you have the following installed:
*   **Python 3.7+**: [Download here](https://www.python.org/downloads/)
*   **Tkinter**: Usually included with Python. If not, install via:
    *   *Windows*: Included by default.
    *   *Linux*: `sudo apt-get install python3-tk`

### 2. Installation & Setup
Clone the repository and enter the project directory:

```bash
# Clone the repository
git clone https://github.com/Tirth0604/AURA_RETAIL_OS.git

# Enter the directory
cd AURA_RETAIL_OS
```

### 3. Running the Dashboard (Recommended)
The **Interactive Intelligence Dashboard** is the primary way to experience the simulation. It provides a real-time audit of design pattern compliance.

```powershell
python gui.py
```
> **Tip:** Once the window opens, click the **"LAUNCH SYSTEM AUDIT"** button to begin the live demonstration.

### 4. Alternative: Terminal Execution
To view the engineering logs directly in your console:
```powershell
python simulation/simulation.py
```
*(Windows Users: If icons do not render, run `$env:PYTHONIOENCODING='utf-8'` first).*

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

## 📂 Project Structure
*   `core/` : Core kiosk logic including Facade and Command patterns.
*   `hardware/` : Hardware abstraction layer and hot-swappable bridge components.
*   `inventory/` : Secure inventory management using Proxy and Composite patterns.
*   `payment/` : Unified payment processing adapters.
*   `persistence/` : Data persistence logic for transactions and inventory.
*   `simulation/` : Executable scenarios proving all system features.
*   `gui.py` : The main Interactive Dashboard entry point.

---

## 👥 Authors (Group 24: Pixel Pioneers)
| Name | Enrollment No. | Primary Responsibility |
| :--- | :--- | :--- |
| **Heer Shah** | 202512024 | Kiosk Core & Facade Architecture |
| **Diya Shah** | 202512025 | Inventory System & Secure Proxy |
| **Tirth Gandhi** | 202512038 | Payment Adapters & Persistence |
| **Nishit Gal** | 202512002 | Hardware Abstraction & Factories |
