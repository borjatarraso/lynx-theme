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

def _to_textual_theme(theme: Theme):
    """Convert a :class:`lynx_theme.model.Theme` to a textual ``Theme``.

    Returns ``None`` if Textual isn't importable, so callers in pure-Tk
    contexts can still use this helper.
    """
    try:
        from textual.theme import Theme as TxTheme
    except Exception:
        return None
    try:
        return TxTheme(
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
    except Exception:
        return None


def register_user_themes(app=None) -> Dict[str, Theme]:
    """Discover user-saved themes and register them everywhere.

    * Returns the ``{name: Theme}`` dict of user themes (built-ins + user JSON).
    * If ``app`` exposes ``register_theme`` (Textual ``App``), each theme is
      registered there so the user can switch to it via the Textual command
      palette / Ctrl+P.
    * If :mod:`lynx_investor_core.gui_themes` is importable, every theme is
      also registered with the Suite-wide Tk theme registry so the
      ``ThemeCycler`` in any Suite GUI picks them up — same JSON file,
      same name, available everywhere.

    Safe to call multiple times — duplicate names are silently ignored.
    """
    out: Dict[str, Theme] = {}

    # Bridge into the Suite-wide Tk theme registry once per process.
    register_gui = None
    try:
        from lynx_investor_core.gui_themes import register_gui_themes as register_gui
    except Exception:
        register_gui = None

    for theme in list_themes():
        out[theme.name] = theme
        tx = _to_textual_theme(theme)
        if tx is None:
            continue
        if app is not None and hasattr(app, "register_theme"):
            try:
                app.register_theme(tx)
            except Exception:
                pass
        if register_gui is not None:
            try:
                register_gui(tx)
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
