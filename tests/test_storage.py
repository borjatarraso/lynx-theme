"""Tests for theme storage: save / load / list / default-pointer."""

from __future__ import annotations

import pytest

from lynx_theme.model import BUILTIN_THEMES, Style, Theme
from lynx_theme.storage import (
    ReadOnlyThemeError,
    clear_default_theme,
    delete_theme,
    get_default_theme_name,
    list_themes,
    load_default_theme,
    load_theme,
    save_theme,
    set_default_theme,
    themes_dir,
)


def _make_theme(name: str) -> Theme:
    return Theme(name=name, description="test",
                 styles={"window": Style(fg="#ffffff", bg="#000000")})


def test_save_and_load_user_theme():
    t = _make_theme("user-one")
    path = save_theme(t)
    assert path.exists()
    loaded = load_theme("user-one")
    assert loaded.name == "user-one"
    assert loaded.builtin is False


def test_save_under_builtin_name_refused():
    with pytest.raises(ReadOnlyThemeError):
        save_theme(Theme(name="lynx-mocha"))


def test_load_builtin_passes_through():
    t = load_theme("lynx-mocha")
    assert t.builtin is True


def test_list_themes_includes_builtins_and_user():
    save_theme(_make_theme("user-two"))
    names = [t.name for t in list_themes()]
    for n in BUILTIN_THEMES:
        assert n in names
    assert "user-two" in names


def test_default_pointer_round_trip():
    save_theme(_make_theme("user-three"))
    set_default_theme("user-three")
    assert get_default_theme_name() == "user-three"
    loaded = load_default_theme()
    assert loaded is not None and loaded.name == "user-three"


def test_set_default_unknown_raises():
    with pytest.raises(FileNotFoundError):
        set_default_theme("ghost-theme")


def test_clear_default():
    save_theme(_make_theme("user-four"))
    set_default_theme("user-four")
    assert clear_default_theme() is True
    assert get_default_theme_name() is None


def test_delete_user_theme():
    save_theme(_make_theme("user-five"))
    assert delete_theme("user-five") is True
    with pytest.raises(FileNotFoundError):
        load_theme("user-five")


def test_delete_builtin_refused():
    with pytest.raises(ReadOnlyThemeError):
        delete_theme("lynx-mocha")
