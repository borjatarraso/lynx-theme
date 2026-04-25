"""Command-line interface for lynx-theme.

Per the design spec the editor itself is **only** available in
graphical or TUI mode. The CLI surface is therefore minimal and
strictly read-only / utility-flavoured:

* ``lynx-theme``          → defaults to the GUI editor.
* ``lynx-theme -tui``     → Textual editor.
* ``lynx-theme -x``       → force the GUI editor.
* ``lynx-theme --list``   → list every theme on disk + the built-ins.
* ``lynx-theme --show NAME``       → print one theme as JSON.
* ``lynx-theme --set-default NAME``→ mark NAME as the Suite default.
* ``lynx-theme --preview NAME``    → render the demo report styled by
                                     NAME to stdout (Rich).
* ``lynx-theme --about``           → about / license.
* ``lynx-theme --version``.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from lynx_theme import APP_NAME, SUITE_LABEL, __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lynx-theme",
        description=(
            "Lynx Theme — visual theme editor for the Lince Investor Suite.\n"
            "The editor runs in graphical (-x) or TUI (-tui) mode only."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  lynx-theme                   Launch the GUI editor (default)\n"
            "  lynx-theme -x                Same — explicit GUI mode\n"
            "  lynx-theme -tui              Launch the Textual TUI editor\n"
            "  lynx-theme --list            List built-in + user themes\n"
            "  lynx-theme --show lynx-mocha Print one theme as JSON\n"
            "  lynx-theme --preview lynx-mocha   Print the demo styled by a theme\n"
            "  lynx-theme --set-default my-theme Set 'my-theme' as the Suite default\n"
            "  lynx-theme --about           Show developer / license info\n"
        ),
    )

    ui = parser.add_mutually_exclusive_group()
    ui.add_argument("-x", "--gui", action="store_true",
                     help="Launch the Tkinter graphical editor (default)")
    ui.add_argument("-tui", "--textual-ui", action="store_true",
                     dest="tui",
                     help="Launch the Textual TUI editor")

    parser.add_argument("--load", metavar="NAME",
                         help="Pre-load NAME as starting point")

    info = parser.add_mutually_exclusive_group()
    info.add_argument("--list", action="store_true",
                       help="List built-in + user themes and exit")
    info.add_argument("--show", metavar="NAME",
                       help="Print one theme's JSON definition and exit")
    info.add_argument("--preview", metavar="NAME",
                       help="Render the demo styled by NAME to stdout")
    info.add_argument("--set-default", metavar="NAME",
                       help="Set NAME as the default theme on Suite startup")
    info.add_argument("--about", action="store_true",
                       help="Show developer / license info and exit")

    parser.add_argument("--version", action="version",
                         version=f"%(prog)s {__version__}  |  {SUITE_LABEL}")

    # Shared --language flag (us / es / it / de / fr / fa).
    try:
        from lynx_investor_core.translations import add_language_argument
        add_language_argument(parser)
    except ImportError:
        pass

    return parser


def run_cli(argv: Optional[list] = None) -> int:
    parser = build_parser()
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args(argv)
    try:
        from lynx_investor_core.translations import apply_args as _apply_lang
        _apply_lang(args)
    except ImportError:
        pass

    if args.about:
        return _cmd_about()
    if args.list:
        return _cmd_list()
    if args.show:
        return _cmd_show(args.show)
    if args.preview:
        return _cmd_preview(args.preview)
    if args.set_default:
        return _cmd_set_default(args.set_default)

    if args.tui:
        from lynx_theme.tui.app import run_tui
        return run_tui(initial_theme=args.load)

    # Default → GUI.
    from lynx_theme.gui.app import run_gui
    return run_gui(initial_theme=args.load)


# ---------------------------------------------------------------------------
# Read-only helpers
# ---------------------------------------------------------------------------

def _cmd_list() -> int:
    from rich.console import Console
    from rich.table import Table
    from rich.box import ROUNDED
    from lynx_theme.storage import list_themes, get_default_theme_name

    console = Console()
    default = get_default_theme_name()
    t = Table(title="Lynx Theme — themes", box=ROUNDED, show_header=True,
              header_style="bold")
    t.add_column("Name", style="bold cyan")
    t.add_column("Type")
    t.add_column("Based On")
    t.add_column("Description", overflow="fold")
    for theme in list_themes():
        kind = "built-in" if theme.builtin else "user"
        marker = "  ⭐ default" if theme.name == default else ""
        t.add_row(theme.name + marker, kind, theme.based_on or "—",
                  theme.description or "")
    console.print(t)
    return 0


def _cmd_show(name: str) -> int:
    from rich.console import Console
    from lynx_theme.storage import load_theme

    console = Console()
    try:
        theme = load_theme(name)
    except FileNotFoundError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        return 1
    print(theme.to_json())
    return 0


def _cmd_preview(name: str) -> int:
    from rich.console import Console
    from lynx_theme.preview import render_preview_into_rich
    from lynx_theme.storage import load_theme

    console = Console()
    try:
        theme = load_theme(name)
    except FileNotFoundError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        return 1
    console.print(render_preview_into_rich(theme))
    return 0


def _cmd_set_default(name: str) -> int:
    from rich.console import Console
    from lynx_theme.storage import set_default_theme

    console = Console()
    try:
        path = set_default_theme(name)
    except FileNotFoundError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        return 1
    console.print(f"[green]✓ '{name}' will load on Suite startup.[/]")
    console.print(f"[dim]Pointer file: {path}[/]")
    return 0


def _cmd_about() -> int:
    from rich.console import Console
    from rich.panel import Panel
    from lynx_theme import get_about_text, get_logo_ascii

    console = Console()
    about = get_about_text()
    logo = get_logo_ascii()
    if logo:
        console.print(Panel(f"[green]{logo}[/]", border_style="green"))
    console.print(Panel(
        f"[bold blue]{about['name']} v{about['version']}[/]\n"
        f"[dim]Part of {about['suite']} v{about['suite_version']}[/]\n"
        f"[dim]Released {about['year']}[/]\n\n"
        f"[bold]Developed by:[/] {about['author']}\n"
        f"[bold]Contact:[/]      {about['email']}\n"
        f"[bold]License:[/]      {about['license']}\n\n"
        f"[dim]{about['description']}[/]",
        title="[bold]About[/]",
        border_style="blue",
    ))
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
