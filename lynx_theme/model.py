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
#
# Some areas are only **advanced** — they're not surfaced by default in
# the editor's compact view, but the user can opt into them via the
# "Show advanced" toggle. They have sensible inherited defaults so the
# theme works fine even if the user never touches them.
BASIC_AREAS: List[str] = [
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
    # Sign-coloured value slots — the +X / -X / X numbers shown in
    # lynx-portfolio P&L lines, gain/loss columns, etc. Surfaced in the
    # editor's main view so users can tune their portfolio's "I'm up /
    # down / flat" feel without diving into Advanced.
    "value_positive",
    "value_negative",
    "value_neutral",
]

ADVANCED_AREAS: List[str] = [
    # Tables / panels
    "table_header",
    "table_border",
    "table_row_alt",
    "panel_border",
    "scrollbar",
    "tooltip",
    # Status & badges
    "status_bar",
    "language_badge",
    "tier_mega",
    "tier_large",
    "tier_mid",
    "tier_small",
    "tier_micro",
    "tier_nano",
    # Verdict / scoring
    "verdict_strong_buy",
    "verdict_buy",
    "verdict_hold",
    "verdict_caution",
    "verdict_avoid",
    # Charts / sparklines
    "chart_positive",
    "chart_negative",
    "chart_neutral",
    "chart_axis",
    # Inputs & focus
    "input_focus",
    "selection",
    "cursor",
    "link",
    # Icons (renderable in GUI; ignored in pure-text TUI)
    "icon_apps",
    "icon_agents",
    "icon_about",
    "icon_quit",
]

# Public ordered list combining both — used by callers that want every key.
AREAS: List[str] = BASIC_AREAS + ADVANCED_AREAS

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
    "value_positive":     "Positive value (+ signed numbers)",
    "value_negative":     "Negative value (− signed numbers)",
    "value_neutral":      "Neutral value (unsigned price / count)",
    # Advanced
    "table_header":       "Table header",
    "table_border":       "Table border",
    "table_row_alt":      "Alternating table row",
    "panel_border":       "Panel border",
    "scrollbar":          "Scrollbar",
    "tooltip":            "Tooltip",
    "status_bar":         "Status bar",
    "language_badge":     "Language toggle badge",
    "tier_mega":          "Tier badge — Mega",
    "tier_large":         "Tier badge — Large",
    "tier_mid":           "Tier badge — Mid",
    "tier_small":         "Tier badge — Small",
    "tier_micro":         "Tier badge — Micro",
    "tier_nano":          "Tier badge — Nano",
    "verdict_strong_buy": "Verdict — Strong Buy",
    "verdict_buy":        "Verdict — Buy",
    "verdict_hold":       "Verdict — Hold",
    "verdict_caution":    "Verdict — Caution",
    "verdict_avoid":      "Verdict — Avoid",
    "chart_positive":     "Chart — positive series",
    "chart_negative":     "Chart — negative series",
    "chart_neutral":      "Chart — neutral series",
    "chart_axis":         "Chart axis / gridlines",
    "input_focus":        "Input field — focus ring",
    "selection":          "Text selection",
    "cursor":             "Caret / cursor",
    "link":               "Hyperlink",
    "icon_apps":          "Icon glyph — Apps",
    "icon_agents":        "Icon glyph — Agents",
    "icon_about":         "Icon glyph — About",
    "icon_quit":          "Icon glyph — Quit",
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
    "value_positive":     "Foreground used for + signed numbers in P&L, gain columns, % change.",
    "value_negative":     "Foreground used for − signed numbers in P&L, loss columns, % change.",
    "value_neutral":      "Foreground for unsigned numbers (price, count, ratios) where direction doesn't apply.",
    "table_header":       "The header row of every Rich Table — bold cyan by default.",
    "table_border":       "The frame around tables.",
    "table_row_alt":      "Every other row's tint, for striped tables.",
    "panel_border":       "The frame around Panels (Verdict, About, Tips).",
    "scrollbar":          "The TUI / Tkinter scrollbar trough + thumb.",
    "tooltip":            "Hover tooltips (e.g. on the language badge).",
    "status_bar":         "Bottom status line in GUIs and TUIs.",
    "language_badge":     "The bottom-right pill that shows EN / ES / IT / DE / FR / FA.",
    "tier_mega":          "Mega-cap / Mega-fund tier badge colour.",
    "tier_large":         "Large-cap / Large-fund tier badge colour.",
    "tier_mid":           "Mid-cap / Mid-fund tier badge colour.",
    "tier_small":         "Small-cap / Small-fund tier badge colour.",
    "tier_micro":         "Micro-cap / Micro-fund tier badge colour.",
    "tier_nano":          "Nano-cap / Nano-fund tier badge colour.",
    "verdict_strong_buy": "The Strong Buy verdict pill / banner.",
    "verdict_buy":        "The Buy verdict pill / banner.",
    "verdict_hold":       "The Hold verdict pill / banner.",
    "verdict_caution":    "The Caution verdict pill / banner.",
    "verdict_avoid":      "The Avoid verdict pill / banner.",
    "chart_positive":     "Sparkline / bar colour for positive returns.",
    "chart_negative":     "Sparkline / bar colour for negative returns.",
    "chart_neutral":      "Sparkline / bar colour for non-signed neutral data.",
    "chart_axis":         "Chart axis lines and gridlines.",
    "input_focus":        "The ring around a focused input field.",
    "selection":          "Selected-text background.",
    "cursor":             "Text-cursor colour.",
    "link":               "Hyperlinks in About / Tips / docs.",
    "icon_apps":          "Foreground colour applied to the dashboard's APP icon glyphs.",
    "icon_agents":        "Foreground colour applied to the dashboard's AGENT icon glyphs.",
    "icon_about":         "Foreground colour for the About-dialog icon.",
    "icon_quit":          "Foreground colour for the Quit-button icon.",
}


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

@dataclass
class IconGlyph:
    """One customisable icon glyph (a Unicode character or short emoji)."""
    glyph: str = ""                # the character, e.g. "📊"
    color: str = "#cdd6f4"         # foreground colour for Tk
    description: str = ""          # human-readable hint shown in the editor

    def to_dict(self) -> Dict[str, Any]:
        return {"glyph": self.glyph, "color": self.color,
                 "description": self.description}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "IconGlyph":
        return cls(
            glyph=str((d or {}).get("glyph", "")),
            color=str((d or {}).get("color", "#cdd6f4")),
            description=str((d or {}).get("description", "")),
        )


# Default glyph map — these are the fallbacks used when a theme doesn't
# override anything. Editors can pick from this set or type any other
# Unicode character.
DEFAULT_ICON_GLYPHS: Dict[str, IconGlyph] = {
    "apps":       IconGlyph(glyph="📊",  color="#89b4fa",
                              description="Dashboard apps"),
    "agents":     IconGlyph(glyph="🤖",  color="#cba6f7",
                              description="Sector agents"),
    "about":      IconGlyph(glyph="ℹ",   color="#a6adc8",
                              description="About / info dialogs"),
    "quit":       IconGlyph(glyph="✕",   color="#f38ba8",
                              description="Quit / close buttons"),
    "save":       IconGlyph(glyph="💾",  color="#a6e3a1",
                              description="Save / export buttons"),
    "load":       IconGlyph(glyph="📂",  color="#f9e2af",
                              description="Load / import buttons"),
    "search":     IconGlyph(glyph="🔍",  color="#94e2d5",
                              description="Search input adornment"),
    "warning":    IconGlyph(glyph="⚠",   color="#f9e2af",
                              description="Warning rows in checklists"),
    "error":      IconGlyph(glyph="✘",   color="#f38ba8",
                              description="Error / fail rows"),
    "success":    IconGlyph(glyph="✓",   color="#a6e3a1",
                              description="Success / pass rows"),
    "info":       IconGlyph(glyph="ⓘ",   color="#89b4fa",
                              description="Info rows"),
    "language":   IconGlyph(glyph="🌐",  color="#cdd6f4",
                              description="Language toggle / picker"),
}


@dataclass
class Theme:
    """A complete Suite theme."""
    name: str = "untitled"
    description: str = ""
    based_on: str = ""                      # original theme used for reference
    styles: Dict[str, Style] = field(default_factory=dict)
    icons: Dict[str, IconGlyph] = field(default_factory=dict)

    # ── Read-only flag ──────────────────────────────────────────────────
    # Built-in / shipped themes are read-only; the editor never overwrites
    # them, only uses them as reference values for new themes.
    builtin: bool = False

    # ── Theme-wide / advanced metadata (all optional) ───────────────────
    author: str = ""                        # human-readable author name
    tags: List[str] = field(default_factory=list)
    spacing: int = 4                        # generic padding base
    border_radius: int = 4                  # rounded-corner radius
    line_height: float = 1.4                # line-height multiplier
    monospace_family: str = "Noto Sans Mono"
    rich_panel_box: str = "rounded"         # rounded / heavy / double
    rtl_default: bool = False               # for FA themes
    high_contrast: bool = False
    reduced_motion: bool = False            # disables marquee / blink
    extra: Dict[str, Any] = field(default_factory=dict)  # forward-compat

    # ── Conveniences ────────────────────────────────────────────────────
    def get(self, area: str) -> Style:
        return self.styles.get(area, Style())

    def set(self, area: str, style: Style) -> None:
        self.styles[area] = style

    def get_icon(self, key: str) -> IconGlyph:
        """Return the icon for *key*, falling back to the package default."""
        if key in self.icons:
            return self.icons[key]
        return DEFAULT_ICON_GLYPHS.get(key, IconGlyph())

    def set_icon(self, key: str, icon: IconGlyph) -> None:
        self.icons[key] = icon

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "based_on": self.based_on,
            "builtin": self.builtin,
            "styles": {k: v.to_dict() for k, v in self.styles.items()},
            "icons": {k: v.to_dict() for k, v in self.icons.items()},
            "author": self.author,
            "tags": list(self.tags),
            "spacing": self.spacing,
            "border_radius": self.border_radius,
            "line_height": self.line_height,
            "monospace_family": self.monospace_family,
            "rich_panel_box": self.rich_panel_box,
            "rtl_default": self.rtl_default,
            "high_contrast": self.high_contrast,
            "reduced_motion": self.reduced_motion,
            "extra": dict(self.extra),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Theme":
        d = d or {}
        styles_raw = d.get("styles") or {}
        styles = {k: Style.from_dict(v) for k, v in styles_raw.items()}
        icons_raw = d.get("icons") or {}
        icons = {k: IconGlyph.from_dict(v) for k, v in icons_raw.items()}
        return cls(
            name=str(d.get("name", "untitled")),
            description=str(d.get("description", "")),
            based_on=str(d.get("based_on", "")),
            builtin=bool(d.get("builtin", False)),
            styles=styles,
            icons=icons,
            author=str(d.get("author", "")),
            tags=list(d.get("tags") or []),
            spacing=int(d.get("spacing", 4) or 4),
            border_radius=int(d.get("border_radius", 4) or 4),
            line_height=float(d.get("line_height", 1.4) or 1.4),
            monospace_family=str(d.get("monospace_family", "Noto Sans Mono")),
            rich_panel_box=str(d.get("rich_panel_box", "rounded")),
            rtl_default=bool(d.get("rtl_default", False)),
            high_contrast=bool(d.get("high_contrast", False)),
            reduced_motion=bool(d.get("reduced_motion", False)),
            extra=dict(d.get("extra") or {}),
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
            "value_positive":    Style(fg="#a6e3a1", bg="#1e1e2e", bold=True, align="right"),
            "value_negative":    Style(fg="#f38ba8", bg="#1e1e2e", bold=True, align="right"),
            "value_neutral":     Style(fg="#cdd6f4", bg="#1e1e2e", align="right"),
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
            "value_positive":    Style(fg="#40a02b", bg="#eff1f5", bold=True, align="right"),
            "value_negative":    Style(fg="#d20f39", bg="#eff1f5", bold=True, align="right"),
            "value_neutral":     Style(fg="#4c4f69", bg="#eff1f5", align="right"),
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
            "value_positive":    Style(fg="#00ff00", bg="#000000", bold=True, align="right"),
            "value_negative":    Style(fg="#ff4040", bg="#000000", bold=True, align="right"),
            "value_neutral":     Style(fg="#ffffff", bg="#000000", bold=True, align="right"),
        },
    )


BUILTIN_THEMES: Dict[str, Theme] = {
    t.name: t for t in (_mocha(), _latte(), _high_contrast())
}
