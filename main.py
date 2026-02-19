"""
Network Status Monitor
======================
A Python desktop application that monitors internet connectivity in real-time
using tkinter for the GUI, requests for connectivity checks, and threading
to keep the UI responsive.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import requests
from datetime import datetime


class NetworkStatusMonitor:
    """Main application class for the Network Status Monitor."""

    # URL and timeout used for connectivity checks
    CHECK_URL = "https://www.google.com"
    CHECK_TIMEOUT = 3          # seconds per request
    CHECK_INTERVAL = 3000      # milliseconds between checks (3 seconds)

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Network Status Monitor")
        self.root.geometry("520x530")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # ── State variables ──────────────────────────────────────────
        self.is_monitoring = False       # True while monitoring loop is active
        self.previous_status = None      # Track last known status for change detection
        self.history: list[str] = []     # Connection history entries
        self._monitor_job = None         # Reference to the scheduled after() job

        # Build the UI
        self._build_ui()

    # ================================================================
    #  UI Construction
    # ================================================================
    def _build_ui(self):
        """Create all GUI widgets with a clean, modern look."""

        # ── Title ────────────────────────────────────────────────────
        title_label = tk.Label(
            self.root,
            text="Network Status Monitor",
            font=("Segoe UI", 20, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e",
        )
        title_label.pack(pady=(18, 4))

        # ── Status indicator ─────────────────────────────────────────
        self.status_label = tk.Label(
            self.root,
            text="⏸  Not Monitoring",
            font=("Segoe UI", 14),
            fg="#a6adc8",
            bg="#1e1e2e",
        )
        self.status_label.pack(pady=(4, 12))

        # ── Button frame ─────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(pady=(0, 12))

        self.start_btn = tk.Button(
            btn_frame,
            text="▶  Start Monitoring",
            font=("Segoe UI", 11, "bold"),
            fg="#1e1e2e",
            bg="#a6e3a1",
            activebackground="#94e090",
            width=18,
            relief="flat",
            cursor="hand2",
            command=self.start_monitoring,
        )
        self.start_btn.grid(row=0, column=0, padx=8)

        self.stop_btn = tk.Button(
            btn_frame,
            text="■  Stop Monitoring",
            font=("Segoe UI", 11, "bold"),
            fg="#1e1e2e",
            bg="#f38ba8",
            activebackground="#e67a97",
            width=18,
            relief="flat",
            cursor="hand2",
            state="disabled",
            command=self.stop_monitoring,
        )
        self.stop_btn.grid(row=0, column=1, padx=8)

        # ── History section ──────────────────────────────────────────
        history_label = tk.Label(
            self.root,
            text="Connection History",
            font=("Segoe UI", 12, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e",
        )
        history_label.pack(anchor="w", padx=20, pady=(4, 2))

        self.history_box = scrolledtext.ScrolledText(
            self.root,
            width=58,
            height=14,
            font=("Consolas", 10),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            state="disabled",          # read-only by default
            wrap="word",
        )
        self.history_box.pack(padx=20, pady=(0, 16))

    # ================================================================
    #  Monitoring Controls
    # ================================================================
    def start_monitoring(self):
        """Begin periodic connectivity checks (prevents duplicate threads)."""
        if self.is_monitoring:
            return  # Already running – ignore duplicate clicks

        self.is_monitoring = True
        self.previous_status = None  # Reset so the first check always logs

        # Update button states
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")

        self._log_history("Monitoring started.")
        self._schedule_check()

    def stop_monitoring(self):
        """Stop the monitoring loop gracefully."""
        self.is_monitoring = False

        # Cancel any pending scheduled check
        if self._monitor_job is not None:
            self.root.after_cancel(self._monitor_job)
            self._monitor_job = None

        # Update button states
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

        self.status_label.configure(text="⏸  Not Monitoring", fg="#a6adc8")
        self._log_history("Monitoring stopped.")

    # ================================================================
    #  Connectivity Check (runs in a background thread)
    # ================================================================
    def _schedule_check(self):
        """Launch a single background check and schedule the next one."""
        if not self.is_monitoring:
            return

        # Run the actual HTTP request in a daemon thread so the UI stays
        # responsive even when the network is slow or unreachable.
        thread = threading.Thread(target=self._check_connection, daemon=True)
        thread.start()

        # Schedule the next check after CHECK_INTERVAL milliseconds
        self._monitor_job = self.root.after(self.CHECK_INTERVAL, self._schedule_check)

    def _check_connection(self):
        """
        Send a GET request to CHECK_URL.
        On success → online; on any exception → offline.
        Results are pushed back to the main thread via root.after().
        """
        try:
            response = requests.get(self.CHECK_URL, timeout=self.CHECK_TIMEOUT)
            # Any successful HTTP response means we have connectivity
            is_online = response.status_code < 400
        except requests.RequestException:
            is_online = False

        # Push the UI update to the main (tkinter) thread
        self.root.after(0, self._update_status, is_online)

    # ================================================================
    #  Status Update & Change Detection
    # ================================================================
    def _update_status(self, is_online: bool):
        """
        Update the status label and, if the state changed, show a popup
        notification and log the event.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_online:
            self.status_label.configure(text="🟢  Online", fg="#a6e3a1")
        else:
            self.status_label.configure(text="🔴  Offline", fg="#f38ba8")

        # ── Detect state change ──────────────────────────────────────
        if self.previous_status is not None and is_online != self.previous_status:
            if is_online:
                msg = f"Internet reconnected at {timestamp}"
                self._log_history(f"🟢 RECONNECTED  — {timestamp}")
                messagebox.showinfo("Network Status", msg)
            else:
                msg = f"Internet disconnected at {timestamp}"
                self._log_history(f"🔴 DISCONNECTED — {timestamp}")
                messagebox.showwarning("Network Status", msg)
        elif self.previous_status is None:
            # First check after monitoring starts – just log, no popup
            status_text = "Online" if is_online else "Offline"
            self._log_history(f"Initial status: {status_text} — {timestamp}")

        self.previous_status = is_online

    # ================================================================
    #  History Logging
    # ================================================================
    def _log_history(self, message: str):
        """Append an entry to the history list and the scrollable text box."""
        self.history.append(message)

        # Enable the text box temporarily to insert text, then disable again
        self.history_box.configure(state="normal")
        self.history_box.insert(tk.END, message + "\n")
        self.history_box.see(tk.END)  # Auto-scroll to the latest entry
        self.history_box.configure(state="disabled")


# ====================================================================
#  Entry Point
# ====================================================================
def main():
    root = tk.Tk()
    NetworkStatusMonitor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
