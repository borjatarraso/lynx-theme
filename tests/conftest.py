"""Shared fixtures: isolate theme storage in a tmpdir for every test."""

from __future__ import annotations

import os
import pytest


@pytest.fixture(autouse=True)
def _isolated_theme_home(tmp_path, monkeypatch):
    """Point LYNX_THEME_HOME at a tmpdir so tests never touch the real config."""
    monkeypatch.setenv("LYNX_THEME_HOME", str(tmp_path))
    yield tmp_path
