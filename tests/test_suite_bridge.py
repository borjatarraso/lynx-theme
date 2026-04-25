"""User-saved JSON themes flow into the Suite-wide GUI registry."""

from __future__ import annotations

import pytest

from lynx_theme.model import Style, Theme
from lynx_theme.storage import register_user_themes, save_theme


@pytest.fixture
def gui_registry():
    """Fresh import + clean the runtime ``_EXTRA_THEMES`` list per test."""
    pytest.importorskip("textual")
    from lynx_investor_core import gui_themes
    gui_themes._EXTRA_THEMES.clear()
    return gui_themes


def _mk(name: str) -> Theme:
    return Theme(
        name=name,
        styles={
            "window":       Style(fg="#abcdef", bg="#101020"),
            "panel":        Style(fg="#abcdef", bg="#202030"),
            "metric_value": Style(fg="#ffaa00", bg="#101020"),
            "subheading":   Style(fg="#aabbcc", bg="#101020"),
            "hero_marquee": Style(fg="#ff44ff", bg="#101020"),
            "success":      Style(fg="#00ff00", bg="#101020"),
            "warning":      Style(fg="#ffff00", bg="#101020"),
            "error":        Style(fg="#ff0000", bg="#101020"),
        },
    )


def test_register_user_themes_bridges_into_gui_registry(gui_registry):
    save_theme(_mk("my-shared-house"))

    # Pre-condition: not registered.
    assert gui_registry.theme_by_name("my-shared-house") is None

    out = register_user_themes()

    assert "my-shared-house" in out
    found = gui_registry.theme_by_name("my-shared-house")
    assert found is not None
    assert found.name == "my-shared-house"
    assert found.background == "#101020"
    assert found.primary == "#ff44ff"


def test_register_user_themes_is_idempotent(gui_registry):
    save_theme(_mk("dup-theme"))
    register_user_themes()
    n1 = len(gui_registry._EXTRA_THEMES)
    register_user_themes()
    n2 = len(gui_registry._EXTRA_THEMES)
    assert n1 == n2, "double-registration should be a no-op"


def test_register_user_themes_works_without_app_argument(gui_registry):
    save_theme(_mk("no-app-needed"))
    out = register_user_themes()  # no app=
    assert "no-app-needed" in out
    assert gui_registry.theme_by_name("no-app-needed") is not None
