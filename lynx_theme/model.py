"""Theme data model.

A :class:`Theme` is a flat dataclass of styled "areas" that drive every
visible bit of a Suite UI. Each area carries a foreground colour, a
background colour, a font family, a font size, and four emphasis flags
(bold, italic, underline, blink). One area also carries a ``marquee``
flag that the GUI / TUI render as a slow horizontal scroll for
hero / banner text.

The areas are deliberately named with end-user vocabulary so the
editor's UI can label them clearly:

* ``window``           — outer window background.
* ``panel``            — inner panel / card background and border.
* ``heading``          — section / table titles.
* ``subheading``       — secondary headings (e.g. tier banner).
* ``metric_label``     — the *name* of a metric (left column of tables).
* ``metric_value``     — the *value* of a metric (right column).
* ``listed_instrument``— ticker / fund-name rows in lists.
* ``description``      — long-form descriptive paragraphs.
* ``warning``          — yellow / orange caution rows.
* ``error``            — red error or fail rows.
* ``success``          — green pass / good-news rows.
* ``muted``            — N/A, dim, helper text.
* ``button``           — primary action buttons.
* ``button_secondary`` — subtle / secondary buttons.
* ``hero_marquee``     — top banner text that may marquee-scroll.

Themes are JSON-serialisable so users can share them as files.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict, List


# ---------------------------------------------------------------------------
# Style atom
# ---------------------------------------------------------------------------

@dataclass
class Style:
    """One styled area: colour + font + emphasis flags."""
    fg: str = "#cdd6f4"           # foreground colour (CSS hex)
    bg: str = "#1e1e2e"           # background colour
    font_family: str = "Noto Sans"
    font_size: int = 11
    bold: bool = False
    italic: bool = False
    underline: bool = False
    blink: bool = False
    marquee: bool = False         # only used by hero_marquee
    align: str = "left"           # "left" | "center" | "right"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Style":
        known = {f.name for f in fields(cls)}
        clean = {k: v for k, v in (d or {}).items() if k in known}
        return cls(**clean)


# Public list of customisable area keys, in display order.
AREAS: List[str] = [
    "window",
    "panel",
    "heading",
    "subheading",
    "metric_label",
    "metric_value",
    "listed_instrument",
    "description",
    "warning",
    "error",
    "success",
    "muted",
    "button",
    "button_secondary",
    "hero_marquee",
]

# End-user-friendly labels for each area.
AREA_LABELS: Dict[str, str] = {
    "window":             "Window background",
    "panel":              "Panel / card",
    "heading":            "Section heading / title",
    "subheading":         "Subheading (tier banners)",
    "metric_label":       "Metric label (left column)",
    "metric_value":       "Metric value (right column)",
    "listed_instrument":  "Listed instrument / ticker row",
    "description":        "Description / long-form paragraph",
    "warning":            "Warning",
    "error":              "Error / fail",
    "success":            "Success / pass",
    "muted":              "Muted / N/A / helper text",
    "button":             "Primary button",
    "button_secondary":   "Secondary button",
    "hero_marquee":       "Hero banner (marquee-capable)",
}

AREA_DESCRIPTIONS: Dict[str, str] = {
    "window":             "The outer window's background colour.",
    "panel":              "Cards, side panels, and the report's framing area.",
    "heading":            "Section titles like 'Costs', 'Performance', 'Allocation'.",
    "subheading":         "Tier banners and sub-sections under a heading.",
    "metric_label":       "Metric names that sit on the left of every metric row.",
    "metric_value":       "Numbers / values shown on the right of every metric row.",
    "listed_instrument":  "Ticker / fund / agent name rows in lists or tables.",
    "description":        "Paragraph copy: descriptions, summaries, education.",
    "warning":            "Caution rows in the passive-investor checklist.",
    "error":              "Fail / red flags / errors.",
    "success":            "Pass / green flags / positive returns.",
    "muted":              "N/A, dim hints, footer text.",
    "button":             "Primary action button (Analyse, Compare, Save).",
    "button_secondary":   "Subtle button (Quit, Back, Cancel).",
    "hero_marquee":       "The top hero banner text. Marquee makes it scroll.",
}


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

@dataclass
class Theme:
    """A complete Suite theme."""
    name: str = "untitled"
    description: str = ""
    based_on: str = ""                      # original theme used for reference
    styles: Dict[str, Style] = field(default_factory=dict)

    # ── Read-only flag ──────────────────────────────────────────────────
    # Built-in / shipped themes are read-only; the editor never overwrites
    # them, only uses them as reference values for new themes.
    builtin: bool = False

    # ── Conveniences ────────────────────────────────────────────────────
    def get(self, area: str) -> Style:
        return self.styles.get(area, Style())

    def set(self, area: str, style: Style) -> None:
        self.styles[area] = style

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "based_on": self.based_on,
            "builtin": self.builtin,
            "styles": {k: v.to_dict() for k, v in self.styles.items()},
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Theme":
        styles_raw = (d or {}).get("styles") or {}
        styles = {k: Style.from_dict(v) for k, v in styles_raw.items()}
        return cls(
            name=str((d or {}).get("name", "untitled")),
            description=str((d or {}).get("description", "")),
            based_on=str((d or {}).get("based_on", "")),
            builtin=bool((d or {}).get("builtin", False)),
            styles=styles,
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, raw: str) -> "Theme":
        return cls.from_dict(json.loads(raw))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^[A-Za-z0-9 _-]{1,40}$")
_HEX_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")


def is_valid_name(name: str) -> bool:
    return bool(_NAME_RE.match(name or ""))


def is_valid_color(color: str) -> bool:
    return bool(_HEX_RE.match((color or "").strip()))


def normalize_color(color: str) -> str:
    s = (color or "").strip()
    if not s:
        return "#000000"
    if not s.startswith("#"):
        s = "#" + s
    return s.lower()


# ---------------------------------------------------------------------------
# Built-in reference themes (read-only — used as starting points only)
# ---------------------------------------------------------------------------

def _mocha() -> Theme:
    """Catppuccin-Mocha-flavoured default — matches the rest of the Suite."""
    return Theme(
        name="lynx-mocha",
        description="Catppuccin Mocha — Suite default dark theme.",
        based_on="",
        builtin=True,
        styles={
            "window":            Style(fg="#cdd6f4", bg="#1e1e2e"),
            "panel":             Style(fg="#cdd6f4", bg="#2a2a3d"),
            "heading":           Style(fg="#89b4fa", bg="#1e1e2e", bold=True, font_size=14),
            "subheading":        Style(fg="#a6adc8", bg="#1e1e2e", bold=True, font_size=12),
            "metric_label":      Style(fg="#cdd6f4", bg="#1e1e2e", bold=True),
            "metric_value":      Style(fg="#f9e2af", bg="#1e1e2e", align="right"),
            "listed_instrument": Style(fg="#89b4fa", bg="#1e1e2e", bold=True),
            "description":       Style(fg="#bac2de", bg="#1e1e2e", italic=False),
            "warning":           Style(fg="#f9e2af", bg="#1e1e2e", bold=True),
            "error":             Style(fg="#f38ba8", bg="#1e1e2e", bold=True),
            "success":           Style(fg="#a6e3a1", bg="#1e1e2e", bold=True),
            "muted":             Style(fg="#6c7086", bg="#1e1e2e", italic=True),
            "button":            Style(fg="#1e1e2e", bg="#89b4fa", bold=True),
            "button_secondary":  Style(fg="#cdd6f4", bg="#45475a"),
            "hero_marquee":      Style(fg="#89b4fa", bg="#1e1e2e",
                                       bold=True, font_size=20, align="center"),
        },
    )


def _latte() -> Theme:
    return Theme(
        name="lynx-latte",
        description="Catppuccin Latte — Suite default light theme.",
        based_on="",
        builtin=True,
        styles={
            "window":            Style(fg="#4c4f69", bg="#eff1f5"),
            "panel":             Style(fg="#4c4f69", bg="#e6e9ef"),
            "heading":           Style(fg="#1e66f5", bg="#eff1f5", bold=True, font_size=14),
            "subheading":        Style(fg="#6c6f85", bg="#eff1f5", bold=True, font_size=12),
            "metric_label":      Style(fg="#4c4f69", bg="#eff1f5", bold=True),
            "metric_value":      Style(fg="#df8e1d", bg="#eff1f5", align="right"),
            "listed_instrument": Style(fg="#1e66f5", bg="#eff1f5", bold=True),
            "description":       Style(fg="#5c5f77", bg="#eff1f5"),
            "warning":           Style(fg="#df8e1d", bg="#eff1f5", bold=True),
            "error":             Style(fg="#d20f39", bg="#eff1f5", bold=True),
            "success":           Style(fg="#40a02b", bg="#eff1f5", bold=True),
            "muted":             Style(fg="#9ca0b0", bg="#eff1f5", italic=True),
            "button":            Style(fg="#eff1f5", bg="#1e66f5", bold=True),
            "button_secondary":  Style(fg="#4c4f69", bg="#ccd0da"),
            "hero_marquee":      Style(fg="#1e66f5", bg="#eff1f5",
                                       bold=True, font_size=20, align="center"),
        },
    )


def _high_contrast() -> Theme:
    return Theme(
        name="lynx-high-contrast",
        description="High-contrast accessibility palette.",
        based_on="",
        builtin=True,
        styles={
            "window":            Style(fg="#ffffff", bg="#000000"),
            "panel":             Style(fg="#ffffff", bg="#101010"),
            "heading":           Style(fg="#ffff00", bg="#000000", bold=True, font_size=15),
            "subheading":        Style(fg="#ffffff", bg="#000000", bold=True, font_size=12),
            "metric_label":      Style(fg="#ffffff", bg="#000000", bold=True),
            "metric_value":      Style(fg="#ffff00", bg="#000000", align="right"),
            "listed_instrument": Style(fg="#00ffff", bg="#000000", bold=True),
            "description":       Style(fg="#ffffff", bg="#000000"),
            "warning":           Style(fg="#ffff00", bg="#000000", bold=True),
            "error":             Style(fg="#ff4040", bg="#000000", bold=True),
            "success":           Style(fg="#00ff00", bg="#000000", bold=True),
            "muted":             Style(fg="#a0a0a0", bg="#000000"),
            "button":            Style(fg="#000000", bg="#ffff00", bold=True),
            "button_secondary":  Style(fg="#ffffff", bg="#404040"),
            "hero_marquee":      Style(fg="#ffff00", bg="#000000",
                                       bold=True, font_size=22, align="center"),
        },
    )


BUILTIN_THEMES: Dict[str, Theme] = {
    t.name: t for t in (_mocha(), _latte(), _high_contrast())
}
