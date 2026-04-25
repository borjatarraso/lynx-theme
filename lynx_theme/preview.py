"""Live theme preview content.

Both the GUI and the TUI use the helpers below to render a small canned
"demo report" in the user's in-progress theme — fund metric rows,
warning / error / success flags, listed tickers, hero banner — so the
user can see how the theme will look in real Suite apps without having
to launch one.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

from lynx_theme.model import Style, Theme


# Each row: (area_key, text). The renderer uses the theme's style for
# that area to lay out the row. Order is deliberate: hero first, then
# heading, then a few metric rows, then the warning / error / success
# flags so every styled area lights up.
DEMO_ROWS: List[Tuple[str, str]] = [
    ("hero_marquee",      "  Lynx Suite Theme Preview  "),
    ("heading",           "Costs"),
    ("metric_label",      "Expense Ratio (TER)"),
    ("metric_value",      "0.04%"),
    ("metric_label",      "Front-End Load"),
    ("metric_value",      "0.00%"),
    ("subheading",        "Performance — last 5 years"),
    ("metric_label",      "5Y CAGR"),
    ("metric_value",      "+12.10%"),
    ("listed_instrument", "VFIAX  ·  Vanguard 500 Index Admiral"),
    ("listed_instrument", "FXAIX  ·  Fidelity 500 Index"),
    ("description",
     "Mutual-fund analysis — share classes, loads, manager tenure, and tax drag."),
    ("success",           "✓ TER below the index-fund threshold"),
    ("warning",           "⚠ Cap-gain distributions averaged 3.2%/yr"),
    ("error",             "✘ Front-load 5.75% — direct return drag"),
    ("muted",             "N/A · helper text · footer caption"),
    ("button",            "[ Analyse ]"),
    ("button_secondary",  "[ Cancel ]"),
]


def demo_lines(theme: Theme) -> List[Tuple[Style, str]]:
    """Return ``[(style, text), …]`` for the demo report under *theme*."""
    out: List[Tuple[Style, str]] = []
    for key, text in DEMO_ROWS:
        out.append((theme.get(key), text))
    return out


# ---------------------------------------------------------------------------
# Tkinter widget helper
# ---------------------------------------------------------------------------

def render_preview_into_tk(parent, theme: Theme) -> None:
    """Render the demo into a Tkinter parent. Used by the GUI editor."""
    import tkinter as tk

    # Wipe previous preview content.
    for w in list(parent.winfo_children()):
        w.destroy()

    bg = theme.get("window").bg
    parent.configure(bg=bg)

    for style, text in demo_lines(theme):
        weight = "bold" if style.bold else "normal"
        slant = "italic" if style.italic else "roman"
        underline = 1 if style.underline else 0
        font_spec = (style.font_family, style.font_size, weight, slant)
        anchor = {"left": "w", "right": "e", "center": "center"}.get(style.align, "w")
        lbl = tk.Label(
            parent,
            text=text,
            fg=style.fg,
            bg=style.bg,
            font=font_spec,
            anchor=anchor,
            padx=8,
            pady=2,
        )
        try:
            lbl.configure(underline=underline)
        except tk.TclError:
            pass
        # Tkinter has no real "blink", so we approximate with a periodic
        # foreground swap when the area has blink=True.
        if style.blink:
            _start_blink(parent, lbl, fg_on=style.fg, fg_off=style.bg)
        # Marquee — slowly shifts the text on hero rows.
        if style.marquee and style.align != "center":
            _start_marquee(parent, lbl, text)
        lbl.pack(fill="x", padx=10)


def _start_blink(parent, lbl, *, fg_on: str, fg_off: str, period_ms: int = 750) -> None:
    state = {"on": True}
    def _tick():
        try:
            if not lbl.winfo_exists():
                return
            state["on"] = not state["on"]
            lbl.configure(fg=fg_on if state["on"] else fg_off)
            parent.after(period_ms, _tick)
        except Exception:
            return
    parent.after(period_ms, _tick)


def _start_marquee(parent, lbl, text: str, *, period_ms: int = 220) -> None:
    pad = "    "
    rolling = pad + text + pad
    state = {"i": 0}
    def _tick():
        try:
            if not lbl.winfo_exists():
                return
            i = state["i"]
            buf = rolling[i:] + rolling[:i]
            lbl.configure(text=buf[:len(rolling)])
            state["i"] = (i + 1) % len(rolling)
            parent.after(period_ms, _tick)
        except Exception:
            return
    parent.after(period_ms, _tick)


# ---------------------------------------------------------------------------
# Rich / textual helper
# ---------------------------------------------------------------------------

def render_preview_into_rich(theme: Theme):
    """Return a Rich renderable with the demo lines styled by *theme*.

    Used by both the TUI editor and a one-shot ``--preview`` CLI dump.
    """
    from rich.console import Group
    from rich.panel import Panel
    from rich.text import Text

    pieces = []
    for style, text in demo_lines(theme):
        rich_style = []
        if style.bold:
            rich_style.append("bold")
        if style.italic:
            rich_style.append("italic")
        if style.underline:
            rich_style.append("underline")
        if style.blink:
            rich_style.append("blink")
        rich_style.append(style.fg)
        rich_style.append(f"on {style.bg}")
        pieces.append(Text(text, style=" ".join(rich_style),
                            justify=style.align if style.align != "left" else None))
    return Panel(
        Group(*pieces),
        title=f"Preview · {theme.name}",
        subtitle="(live)",
    )
