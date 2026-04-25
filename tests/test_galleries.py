"""Tests for the curated icon / palette / font galleries."""

from __future__ import annotations

import re

from lynx_theme.galleries import (
    COLOR_PALETTES,
    FONT_SAMPLE_SENTENCE,
    ICON_GALLERY,
    PREFERRED_FONT_FAMILIES,
    ColorSwatch,
    IconEntry,
    all_icons,
    all_palettes,
    order_fonts,
    palette,
    search_icons,
)


_HEX_RE = re.compile(r"^#[0-9a-f]{6}$")


def test_icon_gallery_has_categories_and_entries():
    assert len(ICON_GALLERY) >= 6
    total = sum(len(v) for v in ICON_GALLERY.values())
    assert total >= 100, f"expected a generous catalog, got {total}"


def test_every_icon_has_glyph_and_name():
    for category, entries in ICON_GALLERY.items():
        assert entries, f"category {category!r} is empty"
        for entry in entries:
            assert isinstance(entry, IconEntry)
            assert entry.glyph, f"empty glyph in {category}"
            assert entry.name, f"empty name in {category}"


def test_search_icons_substring():
    hits = search_icons("chart")
    assert hits, "expected at least one chart icon"
    assert all("chart" in (h.name + " " + " ".join(h.keywords)).lower()
               or "chart" in h.glyph.lower()
               for h in hits)


def test_search_icons_empty_returns_all():
    assert len(search_icons("")) == len(all_icons())
    assert len(search_icons("   ")) == len(all_icons())


def test_color_palettes_have_valid_hex():
    assert len(COLOR_PALETTES) >= 5
    for name, swatches in COLOR_PALETTES.items():
        assert swatches, f"palette {name!r} is empty"
        for sw in swatches:
            assert isinstance(sw, ColorSwatch)
            assert sw.name
            assert _HEX_RE.match(sw.hex), f"bad hex {sw.hex} in {name}"


def test_palette_lookup():
    names = all_palettes()
    assert "Catppuccin Mocha" in names
    assert palette("Catppuccin Mocha")
    assert palette("does-not-exist") == []


def test_order_fonts_surfaces_preferred_first():
    available = ["Random Font A", "Noto Sans", "Random Font B", "DejaVu Sans"]
    ordered = order_fonts(available)
    # The two preferred families come before the unknowns and
    # appear in the order they were declared in PREFERRED_FONT_FAMILIES.
    assert ordered[0] in PREFERRED_FONT_FAMILIES
    assert ordered[1] in PREFERRED_FONT_FAMILIES
    assert "Random Font A" in ordered[2:]
    assert "Random Font B" in ordered[2:]


def test_font_sample_sentence_is_meaty():
    # Need digits, ASCII letters, and at least one symbol so font
    # comparison is meaningful.
    assert any(c.isdigit() for c in FONT_SAMPLE_SENTENCE)
    assert any(c.isalpha() for c in FONT_SAMPLE_SENTENCE)
    assert any(not c.isalnum() and not c.isspace() for c in FONT_SAMPLE_SENTENCE)
    assert len(FONT_SAMPLE_SENTENCE) >= 30
