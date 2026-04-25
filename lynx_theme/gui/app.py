"""Tkinter graphical theme editor for the Lince Investor Suite.

Features the user asked for:

* Catppuccin-Mocha framed editor with the Suite logo and an About dialog.
* One row per customisable area, with friendly labels.
* Fg / bg colour pickers with live swatches.
* Font-family dropdown that previews each option in its own face.
* Font-size spinner.
* Bold / italic / underline / blink / marquee checkboxes.
* Alignment dropdown (left / center / right).
* Top toolbar: Load (read-only when picking a built-in), Save As,
  Set as Default, Live Preview button, Quit.
* Live preview panel docked next to the form, redrawn after every change.
* "Set current theme as default theme" via toolbar button + Ctrl+D shortcut.
"""

from __future__ import annotations

import io
import os
import platform as _plat
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk
from tkinter import font as tkfont
from typing import Optional

from lynx_theme import APP_NAME, SUITE_LABEL, __version__, get_about_text, get_logo_ascii
from lynx_theme.model import (
    AREA_DESCRIPTIONS,
    AREA_LABELS,
    AREAS,
    BUILTIN_THEMES,
    Style,
    Theme,
    is_valid_color,
    is_valid_name,
    normalize_color,
)
from lynx_theme.preview import render_preview_into_tk
from lynx_theme.storage import (
    ReadOnlyThemeError,
    get_default_theme_name,
    list_themes,
    load_theme,
    save_theme,
    set_default_theme,
    themes_dir,
)


# ---------------------------------------------------------------------------
# Suite-aligned palette for the editor itself
# ---------------------------------------------------------------------------
BG = "#1e1e2e"
BG_SURFACE = "#232336"
BG_CARD = "#2a2a3d"
BG_INPUT = "#313147"
FG = "#cdd6f4"
FG_DIM = "#6c7086"
FG_SUBTLE = "#585b70"
ACCENT = "#89b4fa"
BORDER = "#45475a"
GREEN = "#a6e3a1"
RED = "#f38ba8"
YELLOW = "#f9e2af"
BTN_BG = "#89b4fa"
BTN_FG = "#1e1e2e"
BTN_ACTIVE = "#74c7ec"
BTN_SUBTLE = "#45475a"

if _plat.system() == "Windows":
    _FAMILY = "Segoe UI"
elif _plat.system() == "Darwin":
    _FAMILY = "Helvetica"
else:
    _FAMILY = "Noto Sans"

FONT = (_FAMILY, 11)
FONT_BOLD = (_FAMILY, 11, "bold")
FONT_TITLE = (_FAMILY, 22, "bold")
FONT_SMALL = (_FAMILY, 10)
FONT_SECTION = (_FAMILY, 13, "bold")

_IMG_DIR = Path(__file__).resolve().parent.parent.parent / "img"
_LOGO_SM = _IMG_DIR / "logo_sm_quarter_green.png"
_LOGO_MD = _IMG_DIR / "logo_sm_green.png"


# ---------------------------------------------------------------------------
# Colour picker helper
# ---------------------------------------------------------------------------

class _ColorSwatch(tk.Frame):
    """Click-to-pick swatch with a hex value beside it."""
    def __init__(self, parent, *, value: str, on_change):
        super().__init__(parent, bg=BG, highlightthickness=0)
        self._on_change = on_change
        self._value = normalize_color(value)
        self._swatch = tk.Label(self, bg=self._value, width=3, relief="solid",
                                borderwidth=1, cursor="hand2")
        self._swatch.pack(side=tk.LEFT, padx=(0, 6))
        self._var = tk.StringVar(value=self._value)
        self._entry = tk.Entry(self, textvariable=self._var, width=10,
                               bg=BG_INPUT, fg=FG, insertbackground=FG,
                               highlightthickness=1, highlightbackground=BORDER,
                               relief="flat", font=FONT_SMALL)
        self._entry.pack(side=tk.LEFT)
        self._swatch.bind("<Button-1>", self._open_picker)
        self._entry.bind("<Return>", self._apply_text)
        self._entry.bind("<FocusOut>", self._apply_text)

    def _open_picker(self, _event=None):
        try:
            color = colorchooser.askcolor(initialcolor=self._value,
                                          parent=self.winfo_toplevel())
        except tk.TclError:
            return
        if color and color[1]:
            self.set(color[1])
            self._on_change(self._value)

    def _apply_text(self, _event=None):
        candidate = (self._var.get() or "").strip()
        if is_valid_color(candidate):
            self.set(normalize_color(candidate))
            self._on_change(self._value)
        else:
            self._var.set(self._value)

    def set(self, value: str) -> None:
        self._value = normalize_color(value)
        self._var.set(self._value)
        try:
            self._swatch.configure(bg=self._value)
        except tk.TclError:
            pass

    def get(self) -> str:
        return self._value


# ---------------------------------------------------------------------------
# Font-preview helper
# ---------------------------------------------------------------------------

def _available_fonts() -> list[str]:
    try:
        fams = sorted({str(f) for f in tkfont.families() if str(f).strip()})
        # Surface common families first.
        preferred = ["Noto Sans", "Helvetica", "Segoe UI", "DejaVu Sans",
                     "Liberation Sans", "Arial", "Courier New",
                     "Noto Sans Mono", "Menlo", "Consolas",
                     "Times New Roman"]
        head = [f for f in preferred if f in fams]
        tail = [f for f in fams if f not in head]
        return head + tail
    except Exception:
        return ["Noto Sans"]


# ---------------------------------------------------------------------------
# Single area row — compact, aligned, well-spaced
# ---------------------------------------------------------------------------

class _AreaRow(tk.Frame):
    def __init__(self, parent, *, area: str, style: Style, on_change):
        super().__init__(parent, bg=BG, highlightthickness=0)
        self._on_change = on_change
        self._style = style

        label = AREA_LABELS.get(area, area)
        desc = AREA_DESCRIPTIONS.get(area, "")

        # Friendly label + description --------------------------------------
        head = tk.Frame(self, bg=BG)
        head.pack(fill=tk.X)
        tk.Label(head, text=label, font=FONT_BOLD, fg=FG, bg=BG,
                 anchor="w").pack(side=tk.LEFT)
        if desc:
            tk.Label(head, text=f"  — {desc}", font=FONT_SMALL,
                     fg=FG_DIM, bg=BG, anchor="w").pack(side=tk.LEFT)

        # Controls row ------------------------------------------------------
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.X, pady=(2, 0))

        tk.Label(body, text="fg", fg=FG_DIM, bg=BG,
                 font=FONT_SMALL).pack(side=tk.LEFT)
        self._fg = _ColorSwatch(body, value=style.fg, on_change=self._fg_changed)
        self._fg.pack(side=tk.LEFT, padx=(2, 12))

        tk.Label(body, text="bg", fg=FG_DIM, bg=BG,
                 font=FONT_SMALL).pack(side=tk.LEFT)
        self._bg = _ColorSwatch(body, value=style.bg, on_change=self._bg_changed)
        self._bg.pack(side=tk.LEFT, padx=(2, 12))

        tk.Label(body, text="font", fg=FG_DIM, bg=BG,
                 font=FONT_SMALL).pack(side=tk.LEFT)
        self._font_var = tk.StringVar(value=style.font_family)
        font_combo = ttk.Combobox(body, textvariable=self._font_var,
                                  values=_available_fonts(),
                                  width=18, state="readonly")
        font_combo.pack(side=tk.LEFT, padx=(2, 8))
        font_combo.bind("<<ComboboxSelected>>", self._font_changed)

        tk.Label(body, text="size", fg=FG_DIM, bg=BG,
                 font=FONT_SMALL).pack(side=tk.LEFT)
        self._size_var = tk.IntVar(value=style.font_size)
        size_spin = tk.Spinbox(body, from_=6, to=48, width=3,
                                textvariable=self._size_var,
                                bg=BG_INPUT, fg=FG, insertbackground=FG,
                                buttonbackground=BTN_SUBTLE,
                                command=self._size_changed)
        size_spin.pack(side=tk.LEFT, padx=(2, 12))

        tk.Label(body, text="align", fg=FG_DIM, bg=BG,
                 font=FONT_SMALL).pack(side=tk.LEFT)
        self._align_var = tk.StringVar(value=style.align)
        align_combo = ttk.Combobox(body, textvariable=self._align_var,
                                    values=["left", "center", "right"],
                                    width=8, state="readonly")
        align_combo.pack(side=tk.LEFT, padx=(2, 12))
        align_combo.bind("<<ComboboxSelected>>", self._align_changed)

        # Emphasis flags ----------------------------------------------------
        self._bold = tk.BooleanVar(value=style.bold)
        self._italic = tk.BooleanVar(value=style.italic)
        self._underline = tk.BooleanVar(value=style.underline)
        self._blink = tk.BooleanVar(value=style.blink)
        self._marquee = tk.BooleanVar(value=style.marquee)
        for label_text, var in (("Bold", self._bold), ("Italic", self._italic),
                                ("Underline", self._underline),
                                ("Blink", self._blink),
                                ("Marquee", self._marquee)):
            cb = tk.Checkbutton(
                body, text=label_text, variable=var,
                fg=FG, bg=BG, selectcolor=BG_INPUT,
                activebackground=BG, activeforeground=FG,
                font=FONT_SMALL, bd=0, highlightthickness=0,
                command=self._flags_changed,
            )
            cb.pack(side=tk.LEFT, padx=2)

        # Hairline ----------------------------------------------------------
        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill=tk.X, pady=(8, 0))

    # ── Update propagation ────────────────────────────────────────────
    def _fg_changed(self, value: str):
        self._style.fg = value
        self._on_change()

    def _bg_changed(self, value: str):
        self._style.bg = value
        self._on_change()

    def _font_changed(self, _event=None):
        self._style.font_family = self._font_var.get()
        self._on_change()

    def _size_changed(self):
        try:
            self._style.font_size = int(self._size_var.get())
        except (TypeError, ValueError):
            return
        self._on_change()

    def _align_changed(self, _event=None):
        self._style.align = self._align_var.get()
        self._on_change()

    def _flags_changed(self):
        self._style.bold = bool(self._bold.get())
        self._style.italic = bool(self._italic.get())
        self._style.underline = bool(self._underline.get())
        self._style.blink = bool(self._blink.get())
        self._style.marquee = bool(self._marquee.get())
        self._on_change()


# ---------------------------------------------------------------------------
# Splash + style boilerplate (matches Suite vibe)
# ---------------------------------------------------------------------------

def _apply_style(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Lynx.TButton", background=BTN_BG, foreground=BTN_FG,
                    font=(_FAMILY, 10, "bold"), borderwidth=0,
                    padding=(12, 6), relief="flat")
    style.map("Lynx.TButton",
              background=[("active", BTN_ACTIVE), ("pressed", BTN_ACTIVE)])
    style.configure("Subtle.TButton", background=BTN_SUBTLE, foreground=FG,
                    font=(_FAMILY, 10), borderwidth=0,
                    padding=(10, 5), relief="flat")
    style.map("Subtle.TButton",
              background=[("active", BORDER), ("pressed", BORDER)])
    style.configure("TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT,
                    foreground=FG)
    root.option_add("*TCombobox*Listbox.background", BG_INPUT)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.configure(bg=BG)
    return style


# ---------------------------------------------------------------------------
# About dialog
# ---------------------------------------------------------------------------

def _show_about(parent):
    win = tk.Toplevel(parent)
    win.title("About — Lynx Theme")
    win.configure(bg=BG)
    win.geometry("620x520")
    win.transient(parent)

    about = get_about_text()

    if _LOGO_MD.exists():
        try:
            img = tk.PhotoImage(file=str(_LOGO_MD))
            lbl = tk.Label(win, image=img, bg=BG, borderwidth=0)
            lbl.image = img
            lbl.pack(pady=(16, 6))
        except tk.TclError:
            pass

    tk.Label(win, text=f"{about['name']} v{about['version']}",
             font=(_FAMILY, 16, "bold"), bg=BG, fg=ACCENT).pack(pady=(6, 0))
    tk.Label(win, text=f"Part of {about['suite']} v{about['suite_version']}",
             font=FONT_SMALL, bg=BG, fg=FG_DIM).pack()
    tk.Label(win, text=f"Released {about['year']}",
             font=FONT_SMALL, bg=BG, fg=FG_DIM).pack(pady=(0, 12))
    tk.Label(win, text=about["description"], font=FONT_SMALL,
             bg=BG, fg=FG, wraplength=560, justify=tk.LEFT).pack(padx=24, pady=8)
    tk.Label(win, text=f"Developed by: {about['author']}",
             font=FONT_SMALL, bg=BG, fg=FG).pack()
    tk.Label(win, text=f"Contact: {about['email']}",
             font=FONT_SMALL, bg=BG, fg=FG).pack()
    tk.Label(win, text=f"License: {about['license']}",
             font=FONT_SMALL, bg=BG, fg=FG).pack(pady=(0, 12))
    ttk.Button(win, text="Close", style="Lynx.TButton",
               command=win.destroy).pack(pady=(8, 18))
    win.bind("<Escape>", lambda _e: win.destroy())


# ---------------------------------------------------------------------------
# Main GUI
# ---------------------------------------------------------------------------

def run_gui(initial_theme: Optional[str] = None) -> int:
    root = tk.Tk()
    root.title(f"{APP_NAME} v{__version__}")
    root.geometry("1280x900")
    root.minsize(1100, 720)
    _apply_style(root)

    # Working theme — user can swap this with Load.
    state: dict = {
        "theme": _initial_theme(initial_theme),
        "dirty": False,
    }

    # ── Menu ────────────────────────────────────────────────────────────
    menubar = tk.Menu(root, bg=BG_SURFACE, fg=FG, activebackground=ACCENT,
                      activeforeground=BTN_FG, tearoff=0)
    file_menu = tk.Menu(menubar, tearoff=0, bg=BG_SURFACE, fg=FG,
                        activebackground=ACCENT, activeforeground=BTN_FG)
    file_menu.add_command(label="About", command=lambda: _show_about(root))
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=root.quit, accelerator="Ctrl+Q")
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    # ── Hero ────────────────────────────────────────────────────────────
    hero = tk.Frame(root, bg=BG)
    hero.pack(fill=tk.X, padx=16, pady=(14, 8))

    if _LOGO_SM.exists():
        try:
            img = tk.PhotoImage(file=str(_LOGO_SM))
            lbl = tk.Label(hero, image=img, bg=BG, borderwidth=0)
            lbl.image = img
            lbl.pack(side=tk.LEFT, padx=(0, 14))
        except tk.TclError:
            pass

    titles = tk.Frame(hero, bg=BG)
    titles.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Label(titles, text="Lynx Theme", font=FONT_TITLE,
             fg=FG, bg=BG).pack(anchor="w")
    tk.Label(titles, text="Visual theme editor for the Lince Investor Suite",
             font=(_FAMILY, 12), fg=ACCENT, bg=BG).pack(anchor="w")
    tk.Label(titles, text=f"v{__version__}  •  {SUITE_LABEL}",
             font=FONT_SMALL, fg=FG_DIM, bg=BG).pack(anchor="w", pady=(2, 0))

    # Toolbar buttons
    toolbar = tk.Frame(hero, bg=BG)
    toolbar.pack(side=tk.RIGHT)

    name_var = tk.StringVar(value=state["theme"].name)
    based_var = tk.StringVar(value=state["theme"].based_on or "")

    def _toolbar_btn(text, cmd, style="Subtle.TButton", **kw):
        b = ttk.Button(toolbar, text=text, style=style, command=cmd, **kw)
        b.pack(side=tk.LEFT, padx=4)
        return b

    # Toolbar wired below after handlers are defined.
    btn_load = _toolbar_btn("📥  Load", lambda: _on_load())
    btn_save = _toolbar_btn("💾  Save As…", lambda: _on_save_as(),
                            style="Lynx.TButton")
    btn_set_default = _toolbar_btn("⭐  Set as Default",
                                   lambda: _on_set_default())
    btn_preview = _toolbar_btn("👁  Live Preview Window",
                               lambda: _open_preview_window())
    btn_about = _toolbar_btn("About", lambda: _show_about(root))
    btn_quit = _toolbar_btn("Quit", root.quit)

    # ── Identity row (current theme name + based-on) ───────────────────
    ident = tk.Frame(root, bg=BG_SURFACE)
    ident.pack(fill=tk.X, padx=16, pady=(0, 8))
    tk.Label(ident, text="Working theme name:",
             font=FONT_BOLD, fg=FG, bg=BG_SURFACE).pack(side=tk.LEFT, padx=(10, 6),
                                                        pady=8)
    name_entry = tk.Entry(ident, textvariable=name_var,
                           bg=BG_INPUT, fg=FG, insertbackground=FG,
                           font=FONT, width=24, relief="flat")
    name_entry.pack(side=tk.LEFT, padx=(0, 14), pady=8)
    tk.Label(ident, text="Based on:", font=FONT_BOLD, fg=FG_DIM,
             bg=BG_SURFACE).pack(side=tk.LEFT, padx=(0, 6), pady=8)
    tk.Label(ident, textvariable=based_var, font=FONT, fg=ACCENT,
             bg=BG_SURFACE).pack(side=tk.LEFT, padx=(0, 14), pady=8)

    default_lbl_var = tk.StringVar(value=_default_label_text())
    tk.Label(ident, textvariable=default_lbl_var, font=FONT_SMALL,
             fg=GREEN, bg=BG_SURFACE).pack(side=tk.RIGHT, padx=(0, 12), pady=8)

    # ── Body: form (left) + preview (right) ────────────────────────────
    body = tk.Frame(root, bg=BG)
    body.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

    # Form column with vertical scrollbar -------------------------------
    form_wrap = tk.Frame(body, bg=BG, highlightthickness=1,
                          highlightbackground=BORDER)
    form_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

    canvas = tk.Canvas(form_wrap, bg=BG, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(form_wrap, orient=tk.VERTICAL,
                               command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner = tk.Frame(canvas, bg=BG)
    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner_resize(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
    def _on_canvas_resize(event):
        canvas.itemconfigure(inner_id, width=event.width)
    inner.bind("<Configure>", _on_inner_resize)
    canvas.bind("<Configure>", _on_canvas_resize)

    # Mouse-wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120 or (1 if event.delta < 0 else -1)),
                             "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    tk.Label(inner, text="Customisable areas",
             font=FONT_SECTION, fg=ACCENT, bg=BG).pack(anchor="w",
                                                        padx=14, pady=(12, 6))
    tk.Label(inner, text="Each row controls one styled area in the Suite. "
                          "Changes update the live preview on the right.",
             font=FONT_SMALL, fg=FG_DIM, bg=BG, wraplength=720,
             justify=tk.LEFT).pack(anchor="w", padx=14, pady=(0, 12))

    # ── Basic areas (always visible) ────────────────────────────────────
    from lynx_theme.model import BASIC_AREAS, ADVANCED_AREAS, IconGlyph, DEFAULT_ICON_GLYPHS
    rows: list[_AreaRow] = []
    for area in BASIC_AREAS:
        if area not in state["theme"].styles:
            state["theme"].styles[area] = Style()
        row = _AreaRow(inner, area=area, style=state["theme"].styles[area],
                        on_change=lambda: _refresh_preview())
        row.pack(fill=tk.X, padx=14, pady=(8, 0))
        rows.append(row)

    # ── Advanced areas (collapsible) ────────────────────────────────────
    advanced_open = tk.BooleanVar(value=False)
    advanced_frame = tk.Frame(inner, bg=BG)
    advanced_header = tk.Frame(inner, bg=BG)
    advanced_header.pack(fill=tk.X, padx=14, pady=(18, 6))
    tk.Label(advanced_header, text="▼", font=FONT_SECTION,
             fg=ACCENT, bg=BG).pack(side=tk.LEFT, padx=(0, 8))
    tk.Label(advanced_header, text="Advanced areas",
             font=FONT_SECTION, fg=ACCENT, bg=BG).pack(side=tk.LEFT)
    tk.Label(advanced_header,
             text=f"  ({len(ADVANCED_AREAS)} extras: tier badges, verdict pills, "
                  "tables, charts, focus, links, icons …)",
             font=FONT_SMALL, fg=FG_DIM, bg=BG).pack(side=tk.LEFT)

    def _toggle_advanced(*_):
        if advanced_open.get():
            advanced_frame.pack_forget()
            advanced_open.set(False)
            advanced_header.winfo_children()[0].configure(text="▶")
        else:
            advanced_frame.pack(fill=tk.X, padx=0, pady=(0, 0), before=preview_wrap if False else None)
            advanced_open.set(True)
            advanced_header.winfo_children()[0].configure(text="▼")

    for w in advanced_header.winfo_children():
        w.bind("<Button-1>", _toggle_advanced)
    advanced_header.bind("<Button-1>", _toggle_advanced)

    advanced_rows: list[_AreaRow] = []
    for area in ADVANCED_AREAS:
        if area not in state["theme"].styles:
            state["theme"].styles[area] = Style()
        row = _AreaRow(advanced_frame, area=area,
                        style=state["theme"].styles[area],
                        on_change=lambda: _refresh_preview())
        row.pack(fill=tk.X, padx=14, pady=(6, 0))
        advanced_rows.append(row)

    # ── Icon glyph customisation ────────────────────────────────────────
    tk.Label(inner, text="Icon glyphs",
             font=FONT_SECTION, fg=ACCENT, bg=BG).pack(anchor="w",
                                                        padx=14, pady=(18, 6))
    tk.Label(inner, text="Each entry controls a single Unicode glyph that "
                          "appears across the Suite (apps grid, agents grid, "
                          "checklist row icons, language badge, etc.).",
             font=FONT_SMALL, fg=FG_DIM, bg=BG, wraplength=720,
             justify=tk.LEFT).pack(anchor="w", padx=14, pady=(0, 12))

    for icon_key, default_glyph in DEFAULT_ICON_GLYPHS.items():
        # Ensure the theme has an entry we can mutate.
        cur = state["theme"].icons.get(icon_key) or IconGlyph(
            glyph=default_glyph.glyph,
            color=default_glyph.color,
            description=default_glyph.description,
        )
        state["theme"].icons[icon_key] = cur

        row = tk.Frame(inner, bg=BG)
        row.pack(fill=tk.X, padx=14, pady=(6, 0))

        tk.Label(row, text=f"{icon_key}", font=FONT_BOLD,
                 fg=FG, bg=BG, width=12, anchor="w").pack(side=tk.LEFT)

        glyph_var = tk.StringVar(value=cur.glyph)
        glyph_entry = tk.Entry(row, textvariable=glyph_var, width=4,
                                bg=BG_INPUT, fg=FG, insertbackground=FG,
                                font=(_FAMILY, 14), justify="center")
        glyph_entry.pack(side=tk.LEFT, padx=(0, 8))

        def _glyph_changed(_e=None, k=icon_key, v=glyph_var):
            state["theme"].icons[k].glyph = v.get()
            _refresh_preview()
        glyph_entry.bind("<KeyRelease>", _glyph_changed)
        glyph_entry.bind("<FocusOut>", _glyph_changed)

        tk.Label(row, text="colour", font=FONT_SMALL,
                 fg=FG_DIM, bg=BG).pack(side=tk.LEFT)
        sw = _ColorSwatch(row, value=cur.color,
                          on_change=lambda v, k=icon_key: (
                              state["theme"].icons[k].__setattr__("color", v),
                              _refresh_preview(),
                          ))
        sw.pack(side=tk.LEFT, padx=(2, 12))

        tk.Label(row, text=cur.description, font=FONT_SMALL,
                 fg=FG_DIM, bg=BG).pack(side=tk.LEFT, padx=(0, 8))

    # Preview column ----------------------------------------------------
    preview_wrap = tk.Frame(body, bg=BG, highlightthickness=1,
                             highlightbackground=BORDER, width=460)
    preview_wrap.pack(side=tk.RIGHT, fill=tk.BOTH)
    preview_wrap.pack_propagate(False)

    tk.Label(preview_wrap, text="Live Preview",
             font=FONT_SECTION, fg=ACCENT, bg=BG).pack(anchor="w",
                                                        padx=14, pady=(12, 6))
    tk.Label(preview_wrap, text="Updates as you tweak. "
                                  "Use the 'Live Preview Window' button for a "
                                  "free-floating popup.",
             font=FONT_SMALL, fg=FG_DIM, bg=BG, wraplength=420,
             justify=tk.LEFT).pack(anchor="w", padx=14, pady=(0, 8))

    preview_panel = tk.Frame(preview_wrap, bg=BG)
    preview_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    # Status bar --------------------------------------------------------
    status_var = tk.StringVar(value="Ready.")
    status = tk.Label(root, textvariable=status_var, font=FONT_SMALL,
                       fg=FG_DIM, bg=BG, anchor="w")
    status.pack(fill=tk.X, padx=16, pady=(0, 12))

    # ── Behaviour ──────────────────────────────────────────────────────
    def _refresh_preview():
        try:
            render_preview_into_tk(preview_panel, state["theme"])
        except Exception as exc:  # noqa: BLE001
            status_var.set(f"Preview error: {exc}")
            return
        state["dirty"] = True
        status_var.set("Dirty — changes not saved.")
        default_lbl_var.set(_default_label_text())

    def _open_preview_window():
        win = tk.Toplevel(root)
        win.title(f"Preview · {state['theme'].name}")
        win.configure(bg=state["theme"].get("window").bg)
        win.geometry("760x680")
        frame = tk.Frame(win, bg=state["theme"].get("window").bg)
        frame.pack(fill=tk.BOTH, expand=True)
        render_preview_into_tk(frame, state["theme"])
        ttk.Button(win, text="Close", style="Lynx.TButton",
                   command=win.destroy).pack(pady=10)

    def _on_load():
        names = [t.name for t in list_themes()]
        win = tk.Toplevel(root)
        win.title("Load theme")
        win.configure(bg=BG)
        win.transient(root)
        win.geometry("420x420")
        tk.Label(win, text="Load a theme as a starting point",
                 font=FONT_BOLD, fg=FG, bg=BG).pack(pady=(14, 4))
        tk.Label(win, text="Built-in themes are read-only references — saving "
                            "always asks for a new name.",
                 font=FONT_SMALL, fg=FG_DIM, bg=BG, wraplength=380,
                 justify="center").pack(pady=(0, 10), padx=16)
        listbox = tk.Listbox(win, bg=BG_INPUT, fg=FG, selectbackground=ACCENT,
                              selectforeground=BTN_FG, font=FONT,
                              highlightthickness=1, highlightbackground=BORDER,
                              relief="flat")
        for n in names:
            tag = "  (built-in)" if n in BUILTIN_THEMES else ""
            listbox.insert(tk.END, f"{n}{tag}")
        listbox.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))
        if names:
            listbox.selection_set(0)

        def _do_load():
            sel = listbox.curselection()
            if not sel:
                return
            chosen = names[sel[0]]
            try:
                t = load_theme(chosen)
            except FileNotFoundError as exc:
                messagebox.showerror("Load", str(exc), parent=win)
                return
            # Always start a copy so we never mutate the original.
            new = Theme.from_dict(t.to_dict())
            new.name = "untitled"
            new.based_on = chosen
            new.builtin = False
            state["theme"] = new
            _rebuild_rows()
            name_var.set(new.name)
            based_var.set(new.based_on)
            _refresh_preview()
            status_var.set(f"Loaded '{chosen}' as starting point.")
            win.destroy()

        ttk.Button(win, text="Load as starting point",
                   style="Lynx.TButton", command=_do_load).pack(pady=(0, 16))

    def _rebuild_rows():
        for w in list(inner.winfo_children()):
            w.destroy()
        tk.Label(inner, text="Customisable areas",
                 font=FONT_SECTION, fg=ACCENT, bg=BG).pack(anchor="w",
                                                            padx=14, pady=(12, 6))
        tk.Label(inner, text="Each row controls one styled area in the Suite. "
                              "Changes update the live preview on the right.",
                 font=FONT_SMALL, fg=FG_DIM, bg=BG, wraplength=720,
                 justify=tk.LEFT).pack(anchor="w", padx=14, pady=(0, 12))
        rows.clear()
        for area in AREAS:
            if area not in state["theme"].styles:
                state["theme"].styles[area] = Style()
            row = _AreaRow(inner, area=area,
                            style=state["theme"].styles[area],
                            on_change=lambda: _refresh_preview())
            row.pack(fill=tk.X, padx=14, pady=(8, 0))
            rows.append(row)

    def _on_save_as():
        proposed = (name_var.get() or "").strip() or "my-theme"
        new_name = simpledialog.askstring("Save theme",
                                            "Save as (theme name):",
                                            initialvalue=proposed,
                                            parent=root)
        if not new_name:
            return
        new_name = new_name.strip()
        if not is_valid_name(new_name):
            messagebox.showerror("Save",
                                  "Names: letters, digits, spaces, hyphens, "
                                  "underscores; max 40 chars.",
                                  parent=root)
            return
        if new_name in BUILTIN_THEMES:
            messagebox.showerror("Save",
                                  f"'{new_name}' is a built-in theme. "
                                  "Pick a different name.",
                                  parent=root)
            return
        state["theme"].name = new_name
        state["theme"].builtin = False
        try:
            path = save_theme(state["theme"])
        except (ReadOnlyThemeError, ValueError) as exc:
            messagebox.showerror("Save", str(exc), parent=root)
            return
        name_var.set(new_name)
        status_var.set(f"Saved → {path}")
        state["dirty"] = False
        messagebox.showinfo("Save",
                             f"Saved theme '{new_name}' to:\n{path}",
                             parent=root)

    def _on_set_default():
        if state["dirty"]:
            ans = messagebox.askyesno(
                "Unsaved changes",
                "The working theme has unsaved changes. "
                "Save first, then set as default?",
                parent=root,
            )
            if not ans:
                return
            _on_save_as()
            if state["dirty"]:
                return
        try:
            set_default_theme(state["theme"].name)
        except FileNotFoundError as exc:
            messagebox.showerror("Set default", str(exc), parent=root)
            return
        default_lbl_var.set(_default_label_text())
        status_var.set(f"'{state['theme'].name}' set as default theme.")
        messagebox.showinfo("Set default",
                             f"'{state['theme'].name}' will load on Suite startup.",
                             parent=root)

    # Keyboard shortcuts
    root.bind_all("<Control-q>", lambda _e: root.quit())
    root.bind_all("<Control-s>", lambda _e: _on_save_as())
    root.bind_all("<Control-d>", lambda _e: _on_set_default())
    root.bind_all("<Control-l>", lambda _e: _on_load())
    root.bind_all("<Control-p>", lambda _e: _open_preview_window())

    # Language toggle in the bottom-right corner.
    try:
        from lynx_investor_core.lang_widget import mount_tk_language_button
        mount_tk_language_button(
            root,
            on_change=lambda code: status_var.set(f"Language: {code.upper()}"),
            bg=BG_SURFACE, fg=FG, accent=ACCENT,
        )
    except ImportError:
        pass

    # Initial preview render
    _refresh_preview()
    state["dirty"] = False
    status_var.set("Ready.  Ctrl+L = Load · Ctrl+S = Save As · Ctrl+D = Set as Default · Ctrl+P = Preview window")

    root.mainloop()
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _initial_theme(name: Optional[str]) -> Theme:
    if name:
        try:
            t = load_theme(name)
            new = Theme.from_dict(t.to_dict())
            new.name = "untitled"
            new.based_on = name
            new.builtin = False
            return new
        except FileNotFoundError:
            pass
    base = BUILTIN_THEMES["lynx-mocha"]
    new = Theme.from_dict(base.to_dict())
    new.name = "untitled"
    new.based_on = base.name
    new.builtin = False
    return new


def _default_label_text() -> str:
    name = get_default_theme_name()
    if name:
        return f"⭐ default: {name}"
    return "⭐ no default set"
