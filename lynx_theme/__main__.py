"""Entry point for ``python -m lynx_theme`` and the ``lynx-theme`` script."""

from __future__ import annotations

import sys

from lynx_theme.cli import run_cli


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    sys.exit(main())
