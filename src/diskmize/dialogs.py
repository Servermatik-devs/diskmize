"""Secondary windows (About, Help, Updates, Options).

Two defects are fixed here compared to the 0.1 prototype:

* the prototype called ``mainloop()`` inside every ``Toplevel``, which starts a
  second event loop and makes the dialog block the parent window;
* every dialog opened ``logo.png`` with a CWD-relative path.
"""

from __future__ import annotations

import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import ttk

from . import __version__
from .config import Settings
from .i18n import LANGUAGES, translate
from .paths import icon_ico, icon_png

IMAGE_SIZE_SMALL = (75, 75)
IMAGE_SIZE_DIALOG = (150, 150)


def apply_window_icon(window: tk.Misc, *, ico: Path | None = None, png: Path | None = None) -> None:
    """Set a window icon using the mechanism each platform actually supports.

    ``iconbitmap`` raises ``TclError`` with a PNG on X11, and ``iconphoto``
    cannot read an ``.ico``. Keep a reference to the image so Tk does not
    garbage-collect it.
    """
    ico_path = ico if ico is not None else icon_ico()
    png_path = png if png is not None else icon_png()
    try:
        if ico_path.exists() and window.tk.call("tk", "windowingsystem") == "win32":
            window.iconbitmap(default=str(ico_path))
            return
        if png_path.exists():
            image = tk.PhotoImage(file=str(png_path))
            window.iconphoto(True, image)
            window._diskmize_icon = image  # type: ignore[attr-defined]
            return
        if ico_path.exists():
            window.iconbitmap(default=str(ico_path))
    except tk.TclError:
        pass


def load_logo(size: tuple[int, int] = IMAGE_SIZE_DIALOG):
    """Load the logo as a Tk image, returning ``None`` when unavailable."""
    from PIL import Image, ImageTk

    path = icon_png()
    if not path.exists():
        return None
    image = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image)


def center_on_parent(window: tk.Toplevel, parent: tk.Misc) -> None:
    window.update_idletasks()
    width = window.winfo_width() or window.winfo_reqwidth()
    height = window.winfo_height() or window.winfo_reqheight()
    x = max(0, int((parent.winfo_screenwidth() - width) / 2))
    y = max(0, int((parent.winfo_screenheight() - height) / 2))
    window.geometry(f"+{x}+{y}")


def _label(parent: tk.Misc, text: str, *, size: int = 11, wrap: int | None = None) -> ttk.Label:
    widget = ttk.Label(parent, text=text, wraplength=wrap or 0, justify="left")
    widget.configure(font=("TkDefaultFont", size))
    return widget


def _link(parent: tk.Misc, text: str, url: str) -> tk.Label:
    """Create a clickable, keyboard-focusable hyperlink."""
    widget = tk.Label(
        parent,
        text=text,
        fg="#1769aa",
        cursor="hand2",
        font=("TkDefaultFont", 10, "underline"),
        anchor="center",
        takefocus=True,
    )
    widget.bind("<Button-1>", lambda _event: webbrowser.open(url))
    widget.bind("<Return>", lambda _event: webbrowser.open(url))
    widget.bind("<space>", lambda _event: webbrowser.open(url))
    return widget


def about_window(parent: tk.Misc, language: str) -> tk.Toplevel:
    window = tk.Toplevel(parent)
    window.title(translate("about", language))
    window.geometry("460x570")
    window.resizable(False, False)
    apply_window_icon(window)

    _label(window, f"DiskMize v{__version__}", size=18).pack(pady=(16, 6))
    _label(
        window,
        translate("description", language),
        size=10,
        wrap=400,
    ).pack(pady=6, padx=22)

    logo = load_logo()
    if logo is not None:
        holder = ttk.Label(window, image=logo)
        holder.image = logo  # type: ignore[attr-defined]
        holder.pack(pady=6)

    _label(window, translate("author", language), size=11).pack(pady=(6, 4))

    _link(
        window,
        translate("github_label", language),
        "https://github.com/marrionesa",
    ).pack(pady=3)

    _link(
        window,
        translate("email_label", language),
        "mailto:diskmize@marioramos.me",
    ).pack(pady=3)

    _link(
        window,
        translate("license_label", language),
        "https://www.gnu.org/licenses/gpl-3.0.html",
    ).pack(pady=3)

    ttk.Button(
        window,
        text=translate("close", language),
        command=window.destroy,
    ).pack(pady=10)

    center_on_parent(window, parent)
    window.transient(parent)
    window.focus_set()
    return window


def help_window(parent: tk.Misc, language: str) -> tk.Toplevel:
    window = tk.Toplevel(parent)
    window.title(translate("help", language))
    window.geometry("640x600")
    window.minsize(520, 440)
    window.resizable(True, True)
    apply_window_icon(window)

    _label(window, translate("help_intro", language), size=16).pack(pady=(14, 6))

    text = tk.Text(
        window,
        wrap="word",
        height=18,
        width=72,
        borderwidth=1,
        relief="solid",
        padx=12,
        pady=10,
    )
    text.insert("1.0", translate("help_text", language))
    text.configure(state="disabled")
    text.pack(padx=14, pady=8, fill="both", expand=True)

    _link(
        window,
        translate("github_label", language),
        "https://github.com/marrionesa",
    ).pack(pady=2)

    _link(
        window,
        translate("email_label", language),
        "mailto:diskmize@marioramos.me",
    ).pack(pady=2)

    ttk.Button(
        window,
        text=translate("close", language),
        command=window.destroy,
    ).pack(pady=8)

    center_on_parent(window, parent)
    window.transient(parent)
    return window


def updates_window(parent: tk.Misc, language: str) -> tk.Toplevel:
    window = tk.Toplevel(parent)
    window.title(translate("updates", language))
    window.geometry("420x260")
    window.resizable(False, False)
    apply_window_icon(window)

    _label(window, translate("updates", language), size=16).pack(pady=(16, 6))
    _label(
        window, translate("updates_text", language, version=__version__), size=11, wrap=360
    ).pack(pady=10, padx=20)
    ttk.Button(window, text=translate("close", language), command=window.destroy).pack(pady=12)
    center_on_parent(window, parent)
    window.transient(parent)
    return window


def options_window(parent: tk.Misc, settings: Settings, on_save) -> tk.Toplevel:
    """Options dialog. *on_save* receives the edited :class:`Settings`."""
    language = settings.language
    window = tk.Toplevel(parent)
    window.title(translate("options", language))
    window.geometry("460x340")
    window.resizable(False, False)
    apply_window_icon(window)

    _label(window, translate("options", language), size=16).pack(pady=(16, 10))

    frame = ttk.Frame(window, padding=(16, 8))
    frame.pack(fill="both", expand=True)

    _label(frame, translate("language", language)).grid(row=0, column=0, sticky="w", pady=8)
    codes = list(LANGUAGES)
    combo = ttk.Combobox(
        frame, state="readonly", width=22, values=[LANGUAGES[code] for code in codes]
    )
    combo.current(codes.index(language) if language in codes else 0)
    combo.grid(row=0, column=1, sticky="e", pady=8)

    _label(frame, translate("theme", language)).grid(row=1, column=0, sticky="w", pady=8)
    theme_var = tk.StringVar(value=settings.theme)
    ttk.Entry(frame, textvariable=theme_var, width=24).grid(row=1, column=1, sticky="e", pady=8)

    _label(frame, translate("scan_type", language)).grid(row=2, column=0, sticky="w", pady=8)
    scan_var = tk.StringVar(value="full")
    ttk.Combobox(
        frame, state="readonly", width=22, textvariable=scan_var, values=["full", "fast"]
    ).grid(row=2, column=1, sticky="e", pady=8)
    frame.columnconfigure(1, weight=1)

    note = _label(frame, translate("updates_text", language, version=__version__), size=9, wrap=400)
    note.grid(row=3, column=0, columnspan=2, sticky="w", pady=(14, 0))

    def save() -> None:
        new_language = codes[combo.current()] if combo.current() >= 0 else language
        on_save(
            Settings(
                language=new_language,
                theme=theme_var.get().strip() or settings.theme,
                max_rows=settings.max_rows,
            )
        )
        window.destroy()

    buttons = ttk.Frame(window)
    buttons.pack(pady=12)
    ttk.Button(buttons, text=translate("save", language), command=save).pack(side="left", padx=6)
    ttk.Button(buttons, text=translate("close", language), command=window.destroy).pack(
        side="left", padx=6
    )

    center_on_parent(window, parent)
    window.transient(parent)
    window.grab_set()
    return window
