"""Tests for the live preview rendering helper."""

from __future__ import annotations

from lynx_theme.model import BUILTIN_THEMES
from lynx_theme.preview import demo_lines, render_preview_into_rich


def test_demo_lines_cover_every_styled_area():
    theme = BUILTIN_THEMES["lynx-mocha"]
    rows = demo_lines(theme)
    # 1 line per demo row defined in preview.py.
    assert len(rows) >= 14
    for style, text in rows:
        assert isinstance(text, str)
        assert style.fg.startswith("#")
        assert style.bg.startswith("#")


def test_rich_preview_renders_without_error():
    theme = BUILTIN_THEMES["lynx-latte"]
    panel = render_preview_into_rich(theme)
    assert panel is not None
    # The Rich panel exposes a renderable group; just verify it has children.
    inner = getattr(panel.renderable, "renderables", None)
    assert inner is not None and len(inner) >= 1
