"""Tests for the theme dataclass + serialisation."""

from __future__ import annotations

import pytest

from lynx_theme.model import (
    AREAS,
    BUILTIN_THEMES,
    Style,
    Theme,
    is_valid_color,
    is_valid_name,
    normalize_color,
)


def test_areas_list_is_stable():
    # The display + editor depend on these names — guard against accidents.
    assert "window" in AREAS
    assert "metric_label" in AREAS
    assert "warning" in AREAS
    assert "hero_marquee" in AREAS
    assert len(AREAS) >= 12


def test_builtin_themes_are_marked_readonly():
    for theme in BUILTIN_THEMES.values():
        assert theme.builtin is True


def test_style_round_trip():
    s = Style(fg="#ff00ff", bg="#000000", font_size=12, bold=True, marquee=True)
    d = s.to_dict()
    s2 = Style.from_dict(d)
    assert s2 == s


def test_theme_round_trip():
    t = BUILTIN_THEMES["lynx-mocha"]
    raw = t.to_json()
    t2 = Theme.from_json(raw)
    assert t2.name == t.name
    assert set(t2.styles.keys()) == set(t.styles.keys())


def test_validators():
    assert is_valid_name("my theme 1")
    assert is_valid_name("dark_2")
    assert not is_valid_name("")
    assert not is_valid_name("x" * 41)
    assert not is_valid_name("bad/name")

    assert is_valid_color("#abcdef")
    assert is_valid_color("ABCDEF")
    assert not is_valid_color("#abc")
    assert not is_valid_color("not a color")

    assert normalize_color("ABCDEF") == "#abcdef"
    assert normalize_color("#11AAFF") == "#11aaff"
    assert normalize_color("") == "#000000"


def test_theme_get_returns_default_for_unknown_area():
    t = Theme(name="empty")
    s = t.get("never_set")
    assert isinstance(s, Style)
    # Default style is the dark Catppuccin foreground.
    assert s.fg.startswith("#")
