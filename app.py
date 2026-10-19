"""Windows-friendly desktop interface. Run start.bat for automatic setup."""
import os
import json
import queue
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime

from crawler import Worker
from extractor import canonical, is_bluebook
from storage import Store

ROOT = Path(__file__).resolve().parent


class App:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.worker = None
        self.running = False
        self.folder = ""
        self.latest_excel = None
        self.pending_start = None
        root.title("Blue Book • Contact Scraper")
        root.geometry("1120x820")
        root.minsize(900, 680)
        root.configure(bg="#f2f6fb")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f2f6fb")
        style.configure("TLabel", background="#f2f6fb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#183b66")
        style.configure("TButton", padding=(12, 7), font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#f2f6fb", font=("Segoe UI", 10))
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Blue Book Contact Scraper", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text="Find company phones, published emails and named contacts. Save progress automatically.").pack(anchor="w", pady=(5, 14))
        nav = ttk.Frame(frame)
        nav.pack(fill="x")
        ttk.Button(nav, text="1. Open Blue Book", command=self.browse).pack(side="left")
        ttk.Button(nav, text="2. Copy browser URL", command=self.copy_url).pack(side="left", padx=8)
        ttk.Button(nav, text="Import URLs (.txt)", command=self.import_urls).pack(side="left")
        ttk.Button(nav, text="Open latest Excel", command=self.open_latest_excel).pack(side="right")
        ttk.Label(frame, text="3. Search in the browser, then paste results/profile URLs below — one URL per line.").pack(anchor="w", pady=(14, 5))
        self.urls = tk.Text(frame, height=4, font=("Consolas", 10), wrap="word", relief="solid", bd=1)
        self.urls.pack(fill="x")
        self.broad = tk.BooleanVar(value=False)
        self.enrich = tk.BooleanVar(value=True)
        self.retry = tk.BooleanVar(value=True)
        self.autosave = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Discover linked directories/categories too (broader crawl; can take a long time)", variable=self.broad).pack(anchor="w", pady=(8, 2))
        ttk.Checkbutton(frame, text="Check each linked company website for public emails (up to 5 pages/company)", variable=self.enrich).pack(anchor="w")
        ttk.Checkbutton(frame, text="Retry failed pages and refresh saved listing details", variable=self.retry).pack(anchor="w", pady=(2, 8))
        ttk.Checkbutton(frame, text="Keep Excel updated after every completed page (Stop & Save always exports collected data)", variable=self.autosave).pack(anchor="w", pady=(0, 8))
        options = ttk.Frame(frame)
        options.pack(fill="x")
        ttk.Label(options, text="Minimum delay (seconds):").pack(side="left")
        self.delay = ttk.Spinbox(options, from_=5, to=60, width=6)
        self.delay.set("5")
        self.delay.pack(side="left", padx=(8, 20))
        ttk.Label(options, text="Pages per session (0 = no cap):").pack(side="left")
        self.limit = ttk.Spinbox(options, from_=0, to=1000000, width=8)
        self.limit.set("0")
        self.limit.pack(side="left", padx=8)
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=12)
        self.start_button = ttk.Button(actions, text="4. Start / Resume", command=self.start)
        self.start_button.pack(side="left")
        self.pause_button = ttk.Button(actions, text="Pause", command=self.pause)
        self.pause_button.pack(side="left", padx=6)
        ttk.Button(actions, text="Stop & Save", command=self.stop).pack(side="left")
        ttk.Button(actions, text="Continue after access check", command=self.continue_access).pack(side="left", padx=6)
        ttk.Button(actions, text="Open exports", command=self.open_exports).pack(side="right")
        ttk.Button(actions, text="Export saved data", command=self.export).pack(side="right", padx=6)
        self.status = tk.StringVar(value="Ready. Open Blue Book or paste a search-results URL.")
        self.stats = tk.StringVar(value="Companies: 0  |  Completed pages: 0  |  Pending: 0  |  Blocked/errors: 0")
        ttk.Label(frame, textvariable=self.status, foreground="#183b66", wraplength=1030).pack(anchor="w", pady=(0, 6))
        ttk.Label(frame, textvariable=self.stats).pack(anchor="w", pady=(0, 8))
        log_frame = ttk.Frame(frame)
        log_frame.pack(fill="both", expand=True)
        self.log_widget = tk.Text(log_frame, bg="#10243d", fg="#d9e9fa", font=("Consolas", 10), wrap="word", state="disabled", height=10)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_widget.yview)
        self.log_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_widget.pack(fill="both", expand=True)
        ttk.Label(frame, text="Exports: contacts.xlsx • contacts.csv • phones.txt • page audit. Unpublished fields remain blank.", font=("Segoe UI", 9)).pack(anchor="w", pady=(9, 0))
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(150, self.poll)
        self.restore_last_job()

    def restore_last_job(self):
        jobs = list((ROOT / "output").glob("job_*/job.json"))
        if not jobs:
            return
        try:
            path = max(jobs, key=lambda item: item.stat().st_mtime)
            settings = json.loads(path.read_text(encoding="utf-8"))
            seeds = settings.get("seeds", [])
            if not seeds or not all(isinstance(url, str) and is_bluebook(url) for url in seeds):
                return
            self.urls.insert("1.0", "\n".join(seeds))
            self.broad.set(bool(settings.get("directory_discovery", False)))
            self.enrich.set(bool(settings.get("company_website", True)))
            self.folder = str(path.parent)
            summary = path.parent / "run_summary.json"
            if summary.exists():
                exported = json.loads(summary.read_text(encoding="utf-8")).get("excel_file", "contacts.xlsx")
                self.latest_excel = path.parent / Path(exported).name
            self.status.set("Previous job loaded. Click Start / Resume to refresh listings and retry failed pages.")
            self.log("Loaded previous job URLs and options. Existing collected data and queue are retained.")
        except (OSError, ValueError, TypeError):
            self.log("Could not load previous job settings. Paste the results URL to continue.")

    def log(self, value):
        message = f"{datetime.now():%H:%M:%S}  {value}\n"
        self.log_widget.configure(state="normal")
        self.log_widget.insert("end", message)
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")
        if self.folder:
            try:
                with (Path(self.folder) / "run.log").open("a", encoding="utf-8") as handle:
                    handle.write(message)
            except OSError:
                pass

    def ensure_worker(self):
        if not self.worker or not self.worker.is_alive():
            self.worker = Worker(self.events, ROOT)
            self.worker.start()
        return self.worker

    def browse(self):
        if self.running:
            messagebox.showinfo("Crawl running", "Stop & Save before using the browser for a new search.")
            return
        self.ensure_worker().commands.put(("browse", None))

    def copy_url(self):
        if self.running:
            return
        self.ensure_worker().commands.put(("url", None))

    def import_urls(self):
        path = filedialog.askopenfilename(filetypes=[("Text file", "*.txt")])
        if path:
            self.urls.insert("end", "\n" + Path(path).read_text(encoding="utf-8-sig"))

    def start(self):
        if self.running:
            return
        try:
            seeds = [canonical(line.strip()) for line in self.urls.get("1.0", "end").splitlines() if line.strip()]
            if not seeds or any(not u or not is_bluebook(u) for u in seeds):
                raise ValueError("Paste Blue Book results/profile URLs first. Use Open Blue Book, search, then Copy browser URL.")
            delay = float(self.delay.get())
            limit = int(self.limit.get())
            if delay < 5 or delay > 60 or limit < 0:
                raise ValueError("Delay must be 5–60 seconds. Page limit must be 0 or a positive number.")
            if any(u.rstrip("/") == "https://www.thebluebook.com" for u in seeds):
                self.broad.set(True)
                self.log("Homepage selected: linked directory/category discovery is enabled.")
            options = {"seeds": seeds, "delay": delay, "limit": limit, "broad": self.broad.get(), "enrich": self.enrich.get(), "retry": self.retry.get(), "autosave": self.autosave.get()}
        except (ValueError, OverflowError) as exc:
            messagebox.showerror("Check settings", str(exc))
            return
        worker = self.ensure_worker()
        worker.stop_event.clear()
        worker.pause_event.clear()
        self.running = True
        self.start_button.configure(state="disabled")
        self.status.set("Starting browser…")
        worker.commands.put(("crawl", options))

    def pause(self):
        if not self.worker or not self.running:
            return
        if self.worker.pause_event.is_set():
            self.worker.pause_event.clear()
            self.pause_button.configure(text="Pause")
        else:
            self.worker.pause_event.set()
            self.pause_button.configure(text="Resume")
            self.status.set("Pausing after current browser operation…")

    def stop(self):
        if self.worker and self.running:
            self.worker.stop_event.set()
            self.worker.pause_event.clear()
            self.status.set("Stopping and saving… current navigation may take up to 60 seconds.")

    def continue_access(self):
        if self.worker:
            self.worker.resume_event.set()

    def export(self):
        if self.running:
            self.worker.export_event.set()
            self.log("Export requested. Saving at the next browser checkpoint; Stop & Save also exports all collected data.")
            return
        folder = self.folder or filedialog.askdirectory(initialdir=ROOT / "output", title="Select a job folder containing progress.sqlite3")
        if folder:
            try:
                if not (Path(folder) / "progress.sqlite3").is_file():
                    raise ValueError("Select a job folder containing progress.sqlite3; no empty export was created.")
                saved = Store(folder)
                try:
                    recovered = saved.recover_cached_pages()
                    n = saved.export()
                    self.folder = folder
                    self.latest_excel = saved.last_excel_path
                    self.log(f"Exported {n} rows to {saved.last_excel_path}")
                    if not n:
                        messagebox.showinfo("No contacts collected", "The database contains 0 companies. See Summary and Pages in the workbook. Start / Resume with Retry enabled to collect details; exporting alone cannot retrieve unvisited or restricted content.")
                finally:
                    saved.close()
            except Exception as exc:
                messagebox.showerror("Export", str(exc))

    def open_latest_excel(self):
        path = self.latest_excel or (Path(self.folder) / "contacts.xlsx" if self.folder else None)
        if path is None or not path.is_file():
            messagebox.showinfo("No workbook yet", "Start / Resume to collect data, or use Export saved data first.")
            return
        if os.name == "nt":
            os.startfile(path)
        else:
            import subprocess
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])

    def open_exports(self):
        path = self.folder or str(ROOT / "output")
        Path(path).mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(path)
        else:
            import subprocess
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.log(value)
                elif kind == "status":
                    self.status.set(value)
                elif kind == "stats":
                    self.stats.set(f"Companies: {value.get('companies', 0)}  |  Completed pages: {value.get('done', 0)}  |  Pending: {value.get('pending', 0)}  |  Blocked/errors: {value.get('blocked', 0) + value.get('error', 0)}")
                elif kind == "exported":
                    self.latest_excel = Path(value)
                elif kind == "folder":
                    self.folder = value
                elif kind == "attention":
                    self.root.bell()
                elif kind == "url":
                    if is_bluebook(value):
                        current = self.urls.get("1.0", "end").strip()
                        if value not in current.splitlines():
                            self.urls.insert("end", ("\n" if current else "") + value)
                    else:
                        self.log("Navigate to Blue Book results in the open browser first.")
                elif kind in {"finished", "failed"}:
                    self.running = False
                    self.start_button.configure(state="normal")
                    self.pause_button.configure(text="Pause")
                    if kind == "finished":
                        self.status.set(value if isinstance(value, str) else "Finished / saved")
                    if kind == "failed":
                        self.status.set("Browser could not start. See the log.")
        except queue.Empty:
            pass
        self.root.after(150, self.poll)

    def close(self):
        if self.running:
            self.stop()
            self.log("Saving before closing…")
            self.root.after(300, self.finish_close)
        else:
            if self.worker:
                self.worker.commands.put(("quit", None))
            self.root.after(300, self.finish_close)

    def finish_close(self):
        if self.running:
            self.root.after(300, self.finish_close)
        else:
            if self.worker and self.worker.is_alive():
                self.worker.commands.put(("quit", None))
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
