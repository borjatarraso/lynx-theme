"""Tests for the advanced theme model: icons + extra metadata."""

from __future__ import annotations

from lynx_theme.model import (
    ADVANCED_AREAS,
    AREAS,
    BASIC_AREAS,
    BUILTIN_THEMES,
    DEFAULT_ICON_GLYPHS,
    IconGlyph,
    Style,
    Theme,
)


def test_areas_split_into_basic_and_advanced():
    assert set(AREAS) == set(BASIC_AREAS) | set(ADVANCED_AREAS)
    assert len(AREAS) == len(BASIC_AREAS) + len(ADVANCED_AREAS)
    assert "window" in BASIC_AREAS and "window" not in ADVANCED_AREAS
    assert "table_header" in ADVANCED_AREAS and "table_header" not in BASIC_AREAS


def test_default_icon_glyphs_present():
    for key in ("apps", "agents", "about", "quit", "save", "load",
                 "search", "warning", "error", "success", "info", "language"):
        icon = DEFAULT_ICON_GLYPHS.get(key)
        assert icon is not None, f"missing default icon: {key}"
        assert icon.glyph
        assert icon.color.startswith("#")


def test_iconglyph_round_trip():
    g = IconGlyph(glyph="🔥", color="#abcdef", description="hot")
    g2 = IconGlyph.from_dict(g.to_dict())
    assert g == g2


def test_theme_round_trip_with_icons_and_extras():
    t = Theme(
        name="my-advanced",
        styles={"window": Style(fg="#fff", bg="#000")},
        icons={"apps": IconGlyph(glyph="🦊", color="#ff8800",
                                  description="custom apps glyph")},
        author="Borja Tarraso",
        tags=["dark", "custom"],
        spacing=6,
        border_radius=8,
        line_height=1.5,
        monospace_family="Fira Code",
        rich_panel_box="heavy",
        rtl_default=False,
        high_contrast=True,
        reduced_motion=True,
        extra={"custom_key": "custom_value"},
    )
    raw = t.to_json()
    t2 = Theme.from_json(raw)
    assert t2.name == t.name
    assert t2.author == t.author
    assert t2.tags == t.tags
    assert t2.spacing == 6
    assert t2.border_radius == 8
    assert t2.line_height == 1.5
    assert t2.monospace_family == "Fira Code"
    assert t2.rich_panel_box == "heavy"
    assert t2.rtl_default is False
    assert t2.high_contrast is True
    assert t2.reduced_motion is True
    assert t2.extra["custom_key"] == "custom_value"
    assert t2.icons["apps"].glyph == "🦊"
    assert t2.icons["apps"].color == "#ff8800"


def test_get_icon_falls_back_to_default():
    t = Theme(name="x")
    assert t.get_icon("apps").glyph == DEFAULT_ICON_GLYPHS["apps"].glyph
    # Unknown key returns an empty IconGlyph
    assert t.get_icon("ghost").glyph == ""


def test_set_icon_round_trips():
    t = Theme(name="x")
    custom = IconGlyph(glyph="🦄", color="#ff00aa")
    t.set_icon("apps", custom)
    assert t.get_icon("apps") == custom


def test_builtin_themes_still_have_basic_areas():
    # Built-ins predate the advanced split; they only define basic areas.
    for name, theme in BUILTIN_THEMES.items():
        for area in BASIC_AREAS:
            assert area in theme.styles, f"{name} missing {area}"
