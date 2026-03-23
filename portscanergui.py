# ============================================================
#  Network Port Scanner GUI
#  Author  : Aarish Khan
#  AICTE ID: STU6823b63f41f6c1747170879
#  Project : AICTE Internship 2026
#  GitHub  : https://github.com/aarishkhan2361/network-port-scanner
#  License : MIT License
# ============================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import socket
import threading
import time
import queue

# ── Well-known port → service name ──────────────────────────
SERVICE_NAMES = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3",
    143:  "IMAP",
    443:  "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Alt",
}

MAX_THREADS = 500          # concurrent scanning threads
SOCKET_TIMEOUT = 0.5       # seconds per connection attempt


class PortScannerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Network Port Scanner - Aarish Khan | AICTE 2026")
        self.root.resizable(False, False)

        self._stop_event = threading.Event()
        self._result_queue: queue.Queue = queue.Queue()
        self._open_ports: list[int] = []

        self._build_ui()

    # ── UI construction ──────────────────────────────────────
    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        # ── Scan Settings ────────────────────────────────────
        settings = ttk.LabelFrame(self.root, text="Scan Settings")
        settings.grid(row=0, column=0, columnspan=4, sticky="ew", **pad)

        ttk.Label(settings, text="Target (IP / Hostname)").grid(
            row=0, column=0, sticky="w", **pad)
        self.target_var = tk.StringVar(value="8.8.8.8")
        ttk.Entry(settings, textvariable=self.target_var, width=28).grid(
            row=0, column=1, **pad)

        ttk.Label(settings, text="Start").grid(row=0, column=2, sticky="w", **pad)
        self.start_var = tk.StringVar(value="1")
        ttk.Entry(settings, textvariable=self.start_var, width=7).grid(
            row=0, column=3, **pad)

        ttk.Label(settings, text="End Port:").grid(row=0, column=4, sticky="w", **pad)
        self.end_var = tk.StringVar(value="1024")
        ttk.Entry(settings, textvariable=self.end_var, width=7).grid(
            row=0, column=5, **pad)

        self.btn_start = ttk.Button(
            settings, text="Start Scan", command=self._start_scan)
        self.btn_start.grid(row=0, column=6, **pad)

        self.btn_stop = ttk.Button(
            settings, text="Stop", command=self._stop_scan, state="disabled")
        self.btn_stop.grid(row=0, column=7, **pad)

        self.btn_save = ttk.Button(
            settings, text="Save Results", command=self._save_results, state="disabled")
        self.btn_save.grid(row=0, column=8, **pad)

        # ── Status ───────────────────────────────────────────
        status_frame = ttk.LabelFrame(self.root, text="Status")
        status_frame.grid(row=1, column=0, columnspan=4, sticky="ew", **pad)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, width=12).grid(
            row=0, column=0, **pad)

        self.progress = ttk.Progressbar(
            status_frame, orient="horizontal", length=460, mode="determinate")
        self.progress.grid(row=0, column=1, **pad)

        self.time_var = tk.StringVar(value="Elapsed: 0.00s")
        ttk.Label(status_frame, textvariable=self.time_var).grid(
            row=0, column=2, **pad)

        # ── Open Ports ───────────────────────────────────────
        results_frame = ttk.LabelFrame(self.root, text="Open Ports")
        results_frame.grid(row=2, column=0, columnspan=4, **pad)

        self.results_box = scrolledtext.ScrolledText(
            results_frame, width=72, height=16, state="disabled",
            font=("Courier", 10))
        self.results_box.grid(row=0, column=0, **pad)

    # ── Scan control ─────────────────────────────────────────
    def _start_scan(self) -> None:
        target = self.target_var.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target host.")
            return
        try:
            start_port = int(self.start_var.get())
            end_port   = int(self.end_var.get())
            if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
                raise ValueError
            if start_port > end_port:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Ports must be integers between 1 and 65535,\n"
                         "and Start Port must be ≤ End Port.")
            return

        # Resolve hostname once
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            messagebox.showerror("Error", f"Cannot resolve host: {target}")
            return

        self._open_ports.clear()
        self._stop_event.clear()
        self._clear_results()
        self._append_result(
            f"Target: {target} ({ip})\nRange: {start_port}-{end_port}\n\n")

        total = end_port - start_port + 1
        self.progress["maximum"] = total
        self.progress["value"]   = 0
        self.status_var.set("Scanning")
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_save.config(state="disabled")

        self._start_time = time.perf_counter()
        self._scanned    = 0
        self._total      = total

        # Launch scanner thread
        threading.Thread(
            target=self._scan_worker,
            args=(ip, start_port, end_port),
            daemon=True
        ).start()

        # Start UI polling
        self.root.after(100, self._poll_results)

    def _stop_scan(self) -> None:
        self._stop_event.set()

    # ── Core scanning logic ──────────────────────────────────
    def _scan_worker(self, ip: str, start: int, end: int) -> None:
        sem = threading.Semaphore(MAX_THREADS)
        threads = []

        for port in range(start, end + 1):
            if self._stop_event.is_set():
                break
            sem.acquire()
            t = threading.Thread(
                target=self._check_port,
                args=(ip, port, sem),
                daemon=True
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self._result_queue.put(("DONE", None))

    def _check_port(self, ip: str, port: int, sem: threading.Semaphore) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(SOCKET_TIMEOUT)
                if s.connect_ex((ip, port)) == 0:
                    service = SERVICE_NAMES.get(port, "Unknown")
                    self._result_queue.put(("OPEN", (port, service)))
        finally:
            sem.release()
            self._result_queue.put(("PROGRESS", None))

    # ── UI update loop ───────────────────────────────────────
    def _poll_results(self) -> None:
        try:
            while True:
                msg, data = self._result_queue.get_nowait()

                if msg == "OPEN":
                    port, service = data
                    self._open_ports.append(port)
                    self._append_result(f"[+] Port {port} ({service}) is open\n")

                elif msg == "PROGRESS":
                    self._scanned += 1
                    self.progress["value"] = self._scanned
                    elapsed = time.perf_counter() - self._start_time
                    self.time_var.set(f"Elapsed: {elapsed:.2f}s")

                elif msg == "DONE":
                    self._scan_finished()
                    return

        except queue.Empty:
            pass

        self.root.after(100, self._poll_results)

    def _scan_finished(self) -> None:
        elapsed = time.perf_counter() - self._start_time
        count   = len(self._open_ports)
        self._append_result(
            f"\nScan complete.\nOpen ports found: {count}\n")
        self.status_var.set("Completed")
        self.time_var.set(f"Elapsed: {elapsed:.2f}s")
        self.progress["value"] = self._total
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        if count:
            self.btn_save.config(state="normal")

    # ── Results text helpers ─────────────────────────────────
    def _append_result(self, text: str) -> None:
        self.results_box.config(state="normal")
        self.results_box.insert(tk.END, text)
        self.results_box.see(tk.END)
        self.results_box.config(state="disabled")

    def _clear_results(self) -> None:
        self.results_box.config(state="normal")
        self.results_box.delete("1.0", tk.END)
        self.results_box.config(state="disabled")

    # ── Save results ─────────────────────────────────────────
    def _save_results(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save scan results"
        )
        if not path:
            return
        with open(path, "w") as f:
            f.write(self.results_box.get("1.0", tk.END))
        messagebox.showinfo("Saved", f"Results saved to:\n{path}")


# ── Entry point ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()
