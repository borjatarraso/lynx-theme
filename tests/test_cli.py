"""Tests for the CLI parser."""

from __future__ import annotations

import pytest

from lynx_theme.cli import build_parser


def test_help_mentions_theme():
    p = build_parser()
    assert "theme" in p.format_help().lower()


def test_default_no_flags_parses():
    args = build_parser().parse_args([])
    assert args.gui is False
    assert args.tui is False
    assert args.list is False


def test_tui_flag():
    args = build_parser().parse_args(["-tui"])
    assert args.tui is True


def test_gui_flag():
    args = build_parser().parse_args(["-x"])
    assert args.gui is True


def test_ui_modes_mutually_exclusive():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["-x", "-tui"])


def test_info_modes_mutually_exclusive():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--list", "--show", "lynx-mocha"])


def test_set_default_takes_value():
    args = build_parser().parse_args(["--set-default", "my-theme"])
    assert args.set_default == "my-theme"


def test_load_takes_value():
    args = build_parser().parse_args(["--load", "lynx-mocha"])
    assert args.load == "lynx-mocha"


def test_list_command_runs(capsys):
    from lynx_theme.cli import _cmd_list
    rc = _cmd_list()
    assert rc == 0
    out = capsys.readouterr().out
    assert "lynx-mocha" in out


def test_show_command_runs(capsys):
    from lynx_theme.cli import _cmd_show
    rc = _cmd_show("lynx-mocha")
    assert rc == 0
    out = capsys.readouterr().out
    assert "lynx-mocha" in out
    assert "styles" in out


def test_show_unknown_returns_error(capsys):
    from lynx_theme.cli import _cmd_show
    rc = _cmd_show("ghost-theme-name")
    assert rc == 1


def test_preview_command_runs(capsys):
    from lynx_theme.cli import _cmd_preview
    rc = _cmd_preview("lynx-mocha")
    assert rc == 0
    out = capsys.readouterr().out
    assert "Preview" in out
