import tkinter as tk
from tkinter import scrolledtext, ttk
import subprocess
import threading
import sys
import os
import time

class AuraDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Aura Retail OS - Intelligence Dashboard")
        self.root.geometry("1300x850")
        self.root.configure(bg="#0f172a")

        # Design Patterns List
        self.patterns = [
            "Abstract Factory", "Bridge", "Decorator", 
            "Composite", "Proxy", "Adapter", 
            "Command", "Singleton", "Facade"
        ]
        self.pattern_status = {p: False for p in self.patterns}
        self.pattern_widgets = {}

        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1e293b", height=100)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_container = tk.Frame(header_frame, bg="#1e293b")
        title_container.pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Label(
            title_container, text="AURA RETAIL OS", 
            font=("Segoe UI", 20, "bold"), bg="#1e293b", fg="#38bdf8"
        ).pack(anchor="w")
        
        tk.Label(
            title_container, text="PATH B | REAL-TIME ARCHITECTURE AUDIT", 
            font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8"
        ).pack(anchor="w")

        # Main Control
        self.run_btn = tk.Button(
            header_frame, 
            text="▶ LAUNCH SYSTEM AUDIT", 
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7", fg="white",
            activebackground="#0369a1", activeforeground="white",
            relief=tk.FLAT, padx=25, pady=10,
            cursor="hand2", command=self.start_simulation
        )
        self.run_btn.pack(side=tk.RIGHT, padx=30, pady=25)

        # Main Layout
        main_content = tk.Frame(self.root, bg="#0f172a")
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sidebar (Pattern Tracker)
        sidebar = tk.Frame(main_content, bg="#1e293b", width=300)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="PATTERN TRACKER", 
            font=("Segoe UI", 11, "bold"),
            bg="#1e293b", fg="#f1f5f9"
        ).pack(pady=(25, 20))

        for p in self.patterns:
            container = tk.Frame(sidebar, bg="#1e293b", pady=8)
            container.pack(fill=tk.X, padx=25)
            
            icon = tk.Label(container, text="○", font=("Segoe UI", 14), bg="#1e293b", fg="#334155")
            icon.pack(side=tk.LEFT)
            
            lbl = tk.Label(container, text=p, font=("Segoe UI", 10), bg="#1e293b", fg="#64748b")
            lbl.pack(side=tk.LEFT, padx=15)
            
            self.pattern_widgets[p] = {"icon": icon, "label": lbl}

        # Compliance Rating
        stats_frame = tk.Frame(sidebar, bg="#334155", height=120)
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        stats_frame.pack_propagate(False)

        tk.Label(stats_frame, text="COMPLIANCE RATING", font=("Segoe UI", 8, "bold"), bg="#334155", fg="#94a3b8").pack(pady=(15, 5))
        self.progress = ttk.Progressbar(stats_frame, length=200, mode='determinate')
        self.progress.pack(pady=5, padx=20)
        self.percent_lbl = tk.Label(stats_frame, text="0%", font=("Segoe UI", 12, "bold"), bg="#334155", fg="#38bdf8")
        self.percent_lbl.pack()

        # Output Area
        output_frame = tk.Frame(main_content, bg="#0f172a")
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        term_header = tk.Frame(output_frame, bg="#020617", height=35)
        term_header.pack(fill=tk.X)
        tk.Label(term_header, text="CORE_MONITOR.LOG", font=("Consolas", 9), bg="#020617", fg="#475569").pack(side=tk.LEFT, padx=15)

        self.terminal = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 10), 
            bg="#020617", 
            fg="#94a3b8",
            insertbackground="white",
            relief=tk.FLAT,
            padx=25,
            pady=25
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Formatting Tags
        self.terminal.tag_config("scenario", foreground="#38bdf8", font=("Consolas", 14, "bold"))
        self.terminal.tag_config("log", foreground="#eab308")
        self.terminal.tag_config("success", foreground="#22c55e", font=("Consolas", 11, "bold"))
        self.terminal.tag_config("failure", foreground="#ef4444", font=("Consolas", 11, "bold"))
        self.terminal.tag_config("pattern_found", foreground="#818cf8", font=("Consolas", 10, "italic"))

    def update_stats(self):
        found = sum(1 for v in self.pattern_status.values() if v)
        percentage = int((found / len(self.patterns)) * 100)
        self.progress['value'] = percentage
        self.percent_lbl.config(text=f"{percentage}%")

    def activate_pattern(self, pattern_name):
        if not self.pattern_status.get(pattern_name):
            self.pattern_status[pattern_name] = True
            w = self.pattern_widgets[pattern_name]
            w["icon"].config(text="●", fg="#22c55e")
            w["label"].config(fg="#f1f5f9", font=("Segoe UI", 10, "bold"))
            self.update_stats()

    def process_line(self, line):
        for p in self.patterns:
            if p.lower() in line.lower():
                self.activate_pattern(p)

        tag = None
        if "SCENARIO" in line or "====" in line:
            tag = "scenario"
        elif "✓" in line or "SUCCESS" in line or "Success" in line:
            tag = "success"
        elif "✗" in line or "DENIED" in line or "FAILED" in line:
            tag = "failure"
        elif "[" in line and "]" in line:
            tag = "log"

        self.terminal.insert(tk.END, line, tag)
        self.terminal.see(tk.END)

    def start_simulation(self):
        self.terminal.delete(1.0, tk.END)
        self.pattern_status = {p: False for p in self.patterns}
        for p in self.patterns:
            w = self.pattern_widgets[p]
            w["icon"].config(text="○", fg="#334155")
            w["label"].config(fg="#64748b", font=("Segoe UI", 10))
        self.update_stats()
        
        self.run_btn.config(state=tk.DISABLED, text="LOADING SCENARIOS...")
        
        def run():
            script_path = os.path.join(os.path.dirname(__file__), "simulation", "simulation.py")
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            try:
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    env=env,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                self.root.after(0, self.run_btn.config, {"text": "AUDLING ARCHITECTURE..."})
                
                for line in process.stdout:
                    # Send to UI
                    self.root.after(0, self.process_line, line)
                    
                    # DELAY LOGIC:
                    # If it's a major header, pause for 2 seconds to let the user read.
                    if "SCENARIO" in line or "====" in line:
                        time.sleep(2.0)
                    # For normal logs, slow it down to a readable "streaming" pace (0.2 seconds per line)
                    else:
                        time.sleep(0.25)
                
                process.wait()
                self.root.after(0, self.log_finish)
            except Exception as e:
                self.root.after(0, self.process_line, f"\n[CRITICAL ERROR] {str(e)}\n")
            
            self.run_btn.after(0, self.run_btn.config, {"state": tk.NORMAL, "text": "▶ RE-LAUNCH AUDIT"})

        threading.Thread(target=run, daemon=True).start()

    def log_finish(self):
        self.terminal.insert(tk.END, "\n" + "="*60 + "\n", "scenario")
        self.terminal.insert(tk.END, "[SYSTEM] Audit Complete. High Compliance Verified.\n", "success")
        self.terminal.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AuraDashboard(root)
    root.mainloop()
