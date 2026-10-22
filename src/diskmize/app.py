"""Main window.

The 0.1 prototype ran the scan on the UI thread inside a ``while`` loop with
``time.sleep`` and blocked the window while it counted progress. Here every
scan runs in a worker thread and results are handed back to Tk through a queue
polled with ``after``, which is the only thread-safe way to touch Tk widgets.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import APP_NAME, __version__
from .config import Settings, load_settings, save_settings
from .deletion import delete_files
from .dialogs import (
    about_window,
    apply_window_icon,
    help_window,
    load_logo,
    options_window,
    updates_window,
)
from .formatting import format_size, format_timestamp
from .i18n import normalize_language, translate
from .scanner import ScanCancelledError, largest_files, top_folders
from .sysopen import open_path, reveal_path

POLL_INTERVAL_MS = 120
PREVIEW_ROWS = 100


@dataclass
class ScanOutcome:
    kind: str
    entries: list
    errors: list
    cancelled: bool = False


class DiskMizeApp:
    """Tk application controller."""

    def __init__(self, root: tk.Tk, settings: Settings | None = None) -> None:
        self.root = root
        self.settings = settings or load_settings()
        self.language = normalize_language(self.settings.language)
        self._queue: queue.Queue[ScanOutcome] = queue.Queue()
        self._worker: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._row_paths: dict[str, Path] = {}
        self._logo = None
        self._build_ui()
        self._poll_queue()

    # ------------------------------------------------------------------ UI
    def t(self, key: str, **kwargs: object) -> str:
        return translate(key, self.language, **kwargs)

    def _build_ui(self) -> None:
        self.root.title(f"{APP_NAME} v{__version__}")
        self.root.geometry("960x620")
        self.root.minsize(760, 480)
        apply_window_icon(self.root)

        try:
            from ttkthemes import ThemedStyle

            self.style = ThemedStyle(self.root)
            available = self.style.theme_names()
            theme = self.settings.theme if self.settings.theme in available else "clam"
            self.style.set_theme(theme)
        except Exception:  # pragma: no cover - optional dependency path
            self.style = ttk.Style(self.root)

        self._build_menu()
        self._build_statusbar()
        self._build_actions()
        self._build_tree()
        self._center()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.t("options"), command=self.open_options)
        file_menu.add_separator()
        file_menu.add_command(label=self.t("exit"), command=self.root.destroy)
        menubar.add_cascade(label=self.t("menu"), menu=file_menu)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label=self.t("about"), command=self.show_about)
        about_menu.add_separator()
        about_menu.add_command(label=self.t("updates"), command=self.show_updates)
        about_menu.add_separator()
        about_menu.add_command(label=self.t("help"), command=self.show_help)
        menubar.add_cascade(label=self.t("about_menu"), menu=about_menu)
        self.root.config(menu=menubar)

    def _build_statusbar(self) -> None:
        self.status_var = tk.StringVar(value=self.t("ready"))
        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", length=220, mode="indeterminate"
        )
        self.progress.pack(side="bottom", fill="x", padx=10, pady=(0, 6))
        ttk.Label(self.root, textvariable=self.status_var, anchor="w").pack(
            side="bottom", fill="x", padx=12
        )

    def _build_actions(self) -> None:
        bar = ttk.Frame(self.root, padding=(10, 8))
        bar.pack(side="bottom", fill="x")

        self.button_scan_dir = ttk.Button(
            bar, text=self.t("scan_dir"), command=self.choose_directory
        )
        self.button_scan_dir.pack(side="left", padx=4)
        self.button_scan_drive = ttk.Button(
            bar, text=self.t("scan_disk"), command=self.choose_drive
        )
        self.button_scan_drive.pack(side="left", padx=4)
        self.button_stop = ttk.Button(
            bar, text=self.t("stop"), command=self.stop_scan, state="disabled"
        )
        self.button_stop.pack(side="left", padx=4)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)
        self.button_open = ttk.Button(bar, text=self.t("open"), command=self.open_selected)
        self.button_open.pack(side="left", padx=4)
        self.button_reveal = ttk.Button(bar, text=self.t("reveal"), command=self.reveal_selected)
        self.button_reveal.pack(side="left", padx=4)
        self.button_delete = ttk.Button(bar, text=self.t("delete"), command=self.delete_selected)
        self.button_delete.pack(side="left", padx=4)

    def _build_tree(self) -> None:
        container = ttk.Frame(self.root, padding=(10, 6))
        container.pack(fill="both", expand=True)

        sidebar = ttk.Frame(container, padding=(8, 10), relief="groove", borderwidth=1)
        sidebar.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(sidebar, text=f"{APP_NAME} v{__version__}", font=("TkDefaultFont", 13)).pack(
            pady=(4, 8)
        )
        self._logo = load_logo((72, 72))
        if self._logo is not None:
            holder = ttk.Label(sidebar, image=self._logo)
            holder.image = self._logo  # type: ignore[attr-defined]
            holder.pack(pady=(0, 10))

        ttk.Label(sidebar, text=self.t("search_files")).pack(anchor="w", pady=(6, 2))
        self.search_var = tk.StringVar()
        ttk.Entry(sidebar, textvariable=self.search_var, width=22).pack(anchor="w")
        ttk.Button(sidebar, text=self.t("search"), command=self.apply_filter).pack(
            anchor="w", pady=6
        )

        table = ttk.Frame(container)
        table.pack(side="left", fill="both", expand=True)
        ttk.Style(self.root).configure("Treeview", rowheight=24)
        self.tree = ttk.Treeview(table, columns=("size", "modified"), selectmode="extended")
        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.heading("#0", text=self.t("col_name"))
        self.tree.heading("size", text=self.t("col_size"))
        self.tree.heading("modified", text=self.t("col_modified"))
        self.tree.column("#0", width=520, anchor="w")
        self.tree.column("size", width=110, anchor="e")
        self.tree.column("modified", width=150, anchor="e")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda _event: self.open_selected())

    def _center(self) -> None:
        self.root.update_idletasks()
        width, height = 960, 620
        x = max(0, (self.root.winfo_screenwidth() - width) // 2)
        y = max(0, (self.root.winfo_screenheight() - height) // 3)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    # --------------------------------------------------------------- dialect
    def set_language(self, settings: Settings) -> None:
        self.settings = settings
        self.language = normalize_language(settings.language)
        try:
            save_settings(settings)
            message = self.t("ready")
        except OSError:
            message = self.t("error")
        self.status_var.set(message)
        self._retranslate()

    def _retranslate(self) -> None:
        """Rebuild labels in place after a language change."""
        self.button_scan_dir.configure(text=self.t("scan_dir"))
        self.button_scan_drive.configure(text=self.t("scan_disk"))
        self.button_stop.configure(text=self.t("stop"))
        self.button_open.configure(text=self.t("open"))
        self.button_reveal.configure(text=self.t("reveal"))
        self.button_delete.configure(text=self.t("delete"))
        self.tree.heading("#0", text=self.t("col_name"))
        self.tree.heading("size", text=self.t("col_size"))
        self.tree.heading("modified", text=self.t("col_modified"))
        self._build_menu()

    # ---------------------------------------------------------------- scans
    def _ask_directory(self, title: str) -> str | None:
        return filedialog.askdirectory(parent=self.root, title=title) or None

    def choose_directory(self) -> None:
        path = self._ask_directory(self.t("scan_dir"))
        if path:
            self.start_scan("files", path)

    def choose_drive(self) -> None:
        path = self._ask_directory(self.t("scan_disk"))
        if path:
            self.start_scan("folders", path)

    def start_scan(self, kind: str, path: str) -> None:
        if self._worker is not None and self._worker.is_alive():
            return
        self._stop_event = threading.Event()
        self._set_busy(True)
        self.status_var.set(self.t("scanning"))
        self._worker = threading.Thread(
            target=self._run_scan,
            args=(kind, path, self._stop_event),
            name="diskmize-scan",
            daemon=True,
        )
        self._worker.start()

    def _run_scan(self, kind: str, path: str, stop_event: threading.Event) -> None:
        try:
            if kind == "files":
                result = largest_files(path, limit=self.settings.max_rows, stop_event=stop_event)
            else:
                result = top_folders(path, limit=self.settings.max_rows, stop_event=stop_event)
        except ScanCancelledError:
            self._queue.put(ScanOutcome(kind, [], [], cancelled=True))
            return
        except (OSError, ValueError) as exc:
            self._queue.put(ScanOutcome(kind, [], [(path, exc.__class__.__name__)]))
            return
        self._queue.put(ScanOutcome(kind, result.entries, result.errors))

    def stop_scan(self) -> None:
        self._stop_event.set()
        self.status_var.set(self.t("cancelled"))

    def _poll_queue(self) -> None:
        try:
            outcome = self._queue.get_nowait()
        except queue.Empty:
            self.root.after(POLL_INTERVAL_MS, self._poll_queue)
            return
        self._render(outcome)
        self._set_busy(False)
        self.root.after(POLL_INTERVAL_MS, self._poll_queue)

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        for button in (self.button_scan_dir, self.button_scan_drive):
            button.configure(state=state)
        self.button_stop.configure(state="normal" if busy else "disabled")
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _render(self, outcome: ScanOutcome) -> None:
        self.tree.delete(*self.tree.get_children())
        self._row_paths.clear()
        if outcome.cancelled:
            self.status_var.set(self.t("cancelled"))
            return
        show_modified = outcome.kind == "files"
        for entry in outcome.entries[:PREVIEW_ROWS]:
            modified = getattr(entry, "modified", None)
            item = self.tree.insert(
                "",
                "end",
                text=entry.name,
                values=(
                    format_size(entry.size),
                    format_timestamp(modified) if show_modified else "",
                ),
            )
            self._row_paths[item] = entry.path
        message = self.t("done", count=len(outcome.entries))
        if outcome.errors:
            message += " " + self.t("errors", count=len(outcome.errors))
        self.status_var.set(message)

    def apply_filter(self) -> None:
        needle = self.search_var.get().strip().lower()
        for item in self.tree.get_children():
            path = self._row_paths.get(item)
            visible = not needle or (path is not None and needle in path.name.lower())
            self.tree.item(item, tags=() if visible else ("hidden",))
        self.tree.tag_configure("hidden", foreground="")

    # ------------------------------------------------------------- selection
    def selected_paths(self) -> list[Path]:
        return [self._row_paths[item] for item in self.tree.selection() if item in self._row_paths]

    def open_selected(self) -> None:
        paths = self.selected_paths()
        if not paths:
            messagebox.showinfo(self.t("open"), self.t("no_selection"), parent=self.root)
            return
        ok, error = open_path(paths[0])
        if not ok:
            messagebox.showerror(self.t("error"), error, parent=self.root)

    def reveal_selected(self) -> None:
        paths = self.selected_paths()
        if not paths:
            messagebox.showinfo(self.t("reveal"), self.t("no_selection"), parent=self.root)
            return
        ok, error = reveal_path(paths[0])
        if not ok:
            messagebox.showerror(self.t("error"), error, parent=self.root)

    def delete_selected(self) -> None:
        paths = self.selected_paths()
        if not paths:
            messagebox.showinfo(self.t("delete"), self.t("no_selection"), parent=self.root)
            return
        names = "\n".join(f"- {path}" for path in paths[:10])
        if len(paths) > 10:
            names += f"\n... (+{len(paths) - 10})"
        if not messagebox.askyesno(
            self.t("delete_title"), f"{self.t('confirm_delete')}\n\n{names}", parent=self.root
        ):
            return
        outcome = delete_files(paths)
        for item in list(self.tree.selection()):
            path = self._row_paths.get(item)
            if path in outcome.deleted:
                self.tree.delete(item)
                self._row_paths.pop(item, None)
        summary = self.t(
            "deleted", count=outcome.deleted_count, size=format_size(outcome.freed_bytes)
        )
        if outcome.errors:
            summary += "\n" + self.t("delete_errors", count=len(outcome.errors))
        self.status_var.set(summary)
        if outcome.errors:
            details = "\n".join(f"- {path}: {error}" for path, error in outcome.errors)
            messagebox.showwarning(self.t("warning"), f"{summary}\n\n{details}", parent=self.root)

    # ---------------------------------------------------------------- windows
    def show_about(self) -> None:
        about_window(self.root, self.language)

    def show_help(self) -> None:
        help_window(self.root, self.language)

    def show_updates(self) -> None:
        updates_window(self.root, self.language)

    def open_options(self) -> None:
        options_window(self.root, self.settings, self.set_language)

    def run(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self) -> None:
        self._stop_event.set()
        self.root.destroy()


def create_app(settings: Settings | None = None) -> DiskMizeApp:
    root = tk.Tk()
    return DiskMizeApp(root, settings=settings)
