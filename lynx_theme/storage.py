"""Theme persistence: load / save / list / set-default.

Themes live as JSON files under ``$XDG_CONFIG_HOME/lynx-theme/themes/``
(or ``~/.config/lynx-theme/themes/`` if XDG isn't set). The
``LYNX_THEME_HOME`` env var overrides the path entirely (used by tests).

A single ``default.json`` next to the themes folder records the user's
chosen default theme name. The Suite loads that theme on startup if
``register_user_themes`` is wired into a Suite app.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from lynx_theme.model import BUILTIN_THEMES, Theme, is_valid_name


# ---------------------------------------------------------------------------
# Filesystem layout
# ---------------------------------------------------------------------------

def _xdg_config_home() -> Path:
    if os.environ.get("LYNX_THEME_HOME"):
        return Path(os.environ["LYNX_THEME_HOME"])
    if os.environ.get("XDG_CONFIG_HOME"):
        return Path(os.environ["XDG_CONFIG_HOME"]) / "lynx-theme"
    return Path.home() / ".config" / "lynx-theme"


def themes_dir() -> Path:
    p = _xdg_config_home() / "themes"
    p.mkdir(parents=True, exist_ok=True)
    return p


def default_pointer_file() -> Path:
    return _xdg_config_home() / "default.json"


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------

class ReadOnlyThemeError(ValueError):
    """Raised when the user tries to overwrite a built-in (read-only) theme."""


def save_theme(theme: Theme, *, overwrite: bool = False) -> Path:
    if theme.name in BUILTIN_THEMES and not overwrite:
        raise ReadOnlyThemeError(
            f"'{theme.name}' is a built-in reference theme. "
            "Save under a different name."
        )
    if not is_valid_name(theme.name):
        raise ValueError(
            "Theme names may use letters, digits, spaces, hyphens and "
            "underscores only (max 40 chars)."
        )
    path = themes_dir() / f"{theme.name}.json"
    payload = theme.to_dict()
    payload["builtin"] = False
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_theme(name: str) -> Theme:
    """Load by name — built-ins first, then user themes on disk."""
    if name in BUILTIN_THEMES:
        return BUILTIN_THEMES[name]
    path = themes_dir() / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"No theme named '{name}'")
    raw = path.read_text(encoding="utf-8")
    return Theme.from_json(raw)


def list_themes() -> List[Theme]:
    """Built-ins first, then user themes alphabetically."""
    out: List[Theme] = list(BUILTIN_THEMES.values())
    seen = {t.name for t in out}
    if themes_dir().exists():
        for path in sorted(themes_dir().glob("*.json")):
            try:
                t = Theme.from_json(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if t.name in seen:
                continue
            out.append(t)
            seen.add(t.name)
    return out


def delete_theme(name: str) -> bool:
    if name in BUILTIN_THEMES:
        raise ReadOnlyThemeError(
            f"'{name}' is a built-in reference theme and cannot be deleted."
        )
    path = themes_dir() / f"{name}.json"
    if not path.exists():
        return False
    path.unlink()
    return True


# ---------------------------------------------------------------------------
# Default theme pointer
# ---------------------------------------------------------------------------

def get_default_theme_name() -> Optional[str]:
    p = default_pointer_file()
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("default")
    except (json.JSONDecodeError, OSError):
        return None


def set_default_theme(name: str) -> Path:
    """Mark *name* as the default theme loaded by Suite apps on startup."""
    # Ensure the theme actually exists.
    load_theme(name)
    p = default_pointer_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"default": name}, indent=2), encoding="utf-8")
    return p


def clear_default_theme() -> bool:
    p = default_pointer_file()
    if not p.exists():
        return False
    p.unlink()
    return True


def load_default_theme() -> Optional[Theme]:
    name = get_default_theme_name()
    if name is None:
        return None
    try:
        return load_theme(name)
    except FileNotFoundError:
        return None


# ---------------------------------------------------------------------------
# Suite hook
# ---------------------------------------------------------------------------

def register_user_themes(app=None) -> Dict[str, Theme]:
    """Return the user's theme dict. Pass an app object to also register
    them as Textual themes if ``app.register_theme`` is available.
    """
    out: Dict[str, Theme] = {}
    for theme in list_themes():
        out[theme.name] = theme
        if app is not None and hasattr(app, "register_theme"):
            try:
                from textual.theme import Theme as TxTheme
                tx = TxTheme(
                    name=theme.name,
                    primary=theme.get("hero_marquee").fg,
                    secondary=theme.get("subheading").fg,
                    accent=theme.get("metric_value").fg,
                    foreground=theme.get("window").fg,
                    background=theme.get("window").bg,
                    surface=theme.get("panel").bg,
                    panel=theme.get("panel").bg,
                    success=theme.get("success").fg,
                    warning=theme.get("warning").fg,
                    error=theme.get("error").fg,
                    dark=_is_dark(theme.get("window").bg),
                )
                app.register_theme(tx)
            except Exception:
                pass
    return out


def _is_dark(hex_color: str) -> bool:
    s = hex_color.lstrip("#")
    if len(s) != 6:
        return True
    try:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return (r * 0.299 + g * 0.587 + b * 0.114) < 128
    except ValueError:
        return True
