"""Textual TUI theme editor for the Lince Investor Suite.

Same feature set as the GUI editor, presented as a Textual screen:

* List of all customisable areas down the left.
* Per-area editor on the right: fg / bg colour pickers, font dropdown,
  font-size spinner, alignment dropdown, emphasis flags.
* Live Rich preview at the bottom that updates after every edit.
* Top binding bar: ``L`` Load · ``s`` Save As · ``d`` Set as Default ·
  ``p`` Preview Modal · ``a`` About · ``q`` Quit.

Built-in themes are read-only — the editor always saves under a new
name to keep the reference values intact.
"""

from __future__ import annotations

from typing import Optional

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    Select,
    Static,
)
from textual.widgets.option_list import Option

from lynx_theme import APP_NAME, SUITE_LABEL, __version__, get_about_text, get_logo_ascii
from lynx_theme.model import (
    AREA_DESCRIPTIONS,
    AREA_LABELS,
    AREAS,
    BUILTIN_THEMES,
    Style,
    Theme,
    is_valid_color,
    is_valid_name,
    normalize_color,
)
from lynx_theme.preview import render_preview_into_rich
from lynx_theme.storage import (
    ReadOnlyThemeError,
    get_default_theme_name,
    list_themes,
    load_theme,
    save_theme,
    set_default_theme,
)


_FONT_CHOICES = [
    "Default", "Noto Sans", "Helvetica", "Segoe UI", "DejaVu Sans",
    "Courier New", "Noto Sans Mono", "Menlo", "Consolas",
]


# ---------------------------------------------------------------------------
# About modal
# ---------------------------------------------------------------------------

class AboutModal(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss_modal", "Close")]
    DEFAULT_CSS = """
    AboutModal { align: center middle; }
    #about-dialog {
        width: 80%;
        height: 80%;
        max-width: 100;
        background: $surface;
        border: round $primary;
        padding: 1 2;
    }
    #about-title { text-align: center; padding: 1 0; }
    #about-content { padding: 0 1; }
    #about-hint { text-align: center; color: $text-muted; padding-top: 1; }
    """

    def compose(self) -> ComposeResult:
        about = get_about_text()
        logo = get_logo_ascii()
        with Vertical(id="about-dialog"):
            yield Label(f"[bold blue]{about['name']}[/]", id="about-title")
            yield VerticalScroll(
                Static(
                    (f"[green]{logo}[/]\n\n" if logo else "")
                    + f"[bold blue]{about['name']} v{about['version']}[/]\n"
                    f"[dim]Part of {about['suite']} v{about['suite_version']}[/]\n"
                    f"[dim]Released {about['year']}[/]\n\n"
                    f"[bold]Developed by:[/] {about['author']}\n"
                    f"[bold]Contact:[/]      {about['email']}\n"
                    f"[bold]License:[/]      {about['license']}\n\n"
                    f"{about['description']}\n\n"
                    f"[bold cyan]BSD 3-Clause License[/]\n"
                    f"[dim]{about['license_text']}[/]",
                    id="about-content",
                ),
            )
            yield Label("[dim]Press Escape to close[/]", id="about-hint")

    def action_dismiss_modal(self) -> None:
        self.dismiss()


# ---------------------------------------------------------------------------
# Save / Load / Set-default modals
# ---------------------------------------------------------------------------

class _PromptModal(ModalScreen[Optional[str]]):
    """Generic prompt modal returning the entered string (or None)."""
    BINDINGS = [Binding("escape", "_cancel", "Cancel")]
    DEFAULT_CSS = """
    _PromptModal { align: center middle; }
    #dialog { width: 60%; max-width: 80; background: $surface;
              border: round $primary; padding: 1 2; }
    #row { height: auto; align: center middle; padding: 1 0; }
    """

    def __init__(self, title: str, initial: str = "") -> None:
        super().__init__()
        self._title = title
        self._initial = initial

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"[bold]{self._title}[/]")
            yield Input(value=self._initial, id="value")
            with Horizontal(id="row"):
                yield Button("OK", id="ok", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.dismiss(self.query_one("#value", Input).value.strip())
        else:
            self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        self.dismiss(self.query_one("#value", Input).value.strip())

    def action__cancel(self) -> None:
        self.dismiss(None)


class _ChoiceModal(ModalScreen[Optional[str]]):
    """Pick one item from a list."""
    BINDINGS = [Binding("escape", "_cancel", "Cancel")]
    DEFAULT_CSS = """
    _ChoiceModal { align: center middle; }
    #dialog { width: 60%; max-width: 80; height: 60%;
              background: $surface; border: round $primary; padding: 1 2; }
    OptionList { height: 1fr; }
    """

    def __init__(self, title: str, options: list[tuple[str, str]]) -> None:
        super().__init__()
        self._title = title
        self._options = options  # [(label, key)]

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"[bold]{self._title}[/]")
            yield OptionList(*[Option(lbl, id=key) for lbl, key in self._options])
            yield Label("[dim]Enter to pick, Escape to cancel.[/]")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)

    def action__cancel(self) -> None:
        self.dismiss(None)


class _PreviewModal(ModalScreen):
    """Big floating preview with the current theme applied to the demo."""
    BINDINGS = [Binding("escape", "_close", "Close")]
    DEFAULT_CSS = """
    _PreviewModal { align: center middle; }
    #pv-dialog { width: 80%; height: 80%; background: $surface;
                  border: round $primary; padding: 1 2; }
    #pv-title { text-align: center; padding: 1 0; }
    """

    def __init__(self, theme: Theme) -> None:
        super().__init__()
        self._theme = theme

    def compose(self) -> ComposeResult:
        with Vertical(id="pv-dialog"):
            yield Label("[bold]Live Preview[/]", id="pv-title")
            yield VerticalScroll(Static(render_preview_into_rich(self._theme)))
            yield Label("[dim]Press Escape to close[/]")

    def action__close(self) -> None:
        self.dismiss()


# ---------------------------------------------------------------------------
# Main editor app
# ---------------------------------------------------------------------------

class LynxThemeApp(App):
    TITLE = APP_NAME
    SUB_TITLE = SUITE_LABEL

    CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }
    #hero {
        height: 4;
        background: $surface;
        padding: 1 2;
    }
    #body {
        height: 1fr;
    }
    #areas {
        width: 32%;
        border: round $primary;
        padding: 1 1;
    }
    #editor {
        width: 1fr;
        border: round $primary;
        padding: 1 1;
    }
    #preview {
        height: 14;
        border: round $primary;
        padding: 1 1;
    }
    #editor-grid {
        height: auto;
    }
    .row {
        height: auto;
        padding: 0 0 1 0;
    }
    Label {
        padding: 0 1;
    }
    Input {
        width: 16;
    }
    Select {
        width: 22;
    }
    """

    BINDINGS = [
        Binding("L", "load_theme", "Load"),
        Binding("s", "save_as", "Save As"),
        Binding("d", "set_default", "Set Default"),
        Binding("p", "preview_modal", "Preview"),
        Binding("a", "about", "About"),
        Binding("g", "cycle_language", "Language"),
        Binding("q", "quit", "Quit"),
    ]

    def action_cycle_language(self) -> None:
        try:
            from lynx_investor_core.translations import (
                cycle_language, language_full_name,
            )
            new_code = cycle_language()
            self.notify(f"Language → {language_full_name(new_code)} ({new_code.upper()})",
                         timeout=3)
        except ImportError:
            self.notify("Language switching unavailable.", severity="warning",
                         timeout=2)

    def __init__(self, initial_theme: Optional[str] = None) -> None:
        super().__init__()
        self._theme = self._make_initial(initial_theme)
        self._current_area = AREAS[0]

    # ── Compose ────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(
            (
                f"[bold blue]Lynx Theme[/] v{__version__}    "
                f"[dim]Working theme:[/] [bold]{self._theme.name}[/]    "
                f"[dim]Based on:[/] [italic]{self._theme.based_on or '—'}[/]    "
                f"[dim]Default:[/] [bold]{get_default_theme_name() or 'none'}[/]"
            ),
            id="hero",
        )
        with Horizontal(id="body"):
            yield ListView(
                *[ListItem(Label(AREA_LABELS.get(a, a)), id=a) for a in AREAS],
                id="areas",
            )
            with VerticalScroll(id="editor"):
                yield Vertical(id="editor-grid")
        yield Static(id="preview")
        yield Footer()

    # ── Lifecycle ──────────────────────────────────────────────────────
    def on_mount(self) -> None:
        try:
            self.theme = "textual-dark"
        except Exception:
            pass
        listview = self.query_one("#areas", ListView)
        listview.index = 0
        self._render_editor(self._current_area)
        self._render_preview()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        self._current_area = event.item.id or AREAS[0]
        self._render_editor(self._current_area)

    # ── Editor pane ────────────────────────────────────────────────────
    def _render_editor(self, area: str) -> None:
        grid = self.query_one("#editor-grid", Vertical)
        grid.remove_children()
        if area not in self._theme.styles:
            self._theme.styles[area] = Style()
        s = self._theme.styles[area]

        grid.mount(Static(f"[bold]{AREA_LABELS.get(area, area)}[/]"))
        grid.mount(Static(f"[dim]{AREA_DESCRIPTIONS.get(area, '')}[/]"))
        grid.mount(Static(""))

        # Foreground / background --------------------------------------
        grid.mount(Static("[bold]Foreground colour (hex)[/]"))
        grid.mount(Input(value=s.fg, id="fg"))
        grid.mount(Static("[bold]Background colour (hex)[/]"))
        grid.mount(Input(value=s.bg, id="bg"))

        # Font family / size -------------------------------------------
        font_options = [(f, f) for f in _FONT_CHOICES]
        if s.font_family not in {f for f, _ in font_options}:
            font_options.insert(0, (s.font_family, s.font_family))
        grid.mount(Static("[bold]Font family[/]"))
        grid.mount(Select(font_options, value=s.font_family,
                           id="font_family", allow_blank=False))
        grid.mount(Static("[bold]Font size[/]"))
        grid.mount(Input(value=str(s.font_size), id="font_size"))

        # Alignment + emphasis -----------------------------------------
        grid.mount(Static("[bold]Alignment[/]"))
        grid.mount(Select([("Left", "left"), ("Center", "center"), ("Right", "right")],
                           value=s.align, id="align", allow_blank=False))
        grid.mount(Static("[bold]Emphasis[/]"))
        grid.mount(Checkbox("Bold", value=s.bold, id="bold"))
        grid.mount(Checkbox("Italic", value=s.italic, id="italic"))
        grid.mount(Checkbox("Underline", value=s.underline, id="underline"))
        grid.mount(Checkbox("Blink", value=s.blink, id="blink"))
        grid.mount(Checkbox("Marquee", value=s.marquee, id="marquee"))

        grid.mount(Static(""))
        grid.mount(Static("[dim]Tip: built-in themes are read-only — "
                            "any save will create a new theme by name.[/]"))

    def _current_style(self) -> Style:
        if self._current_area not in self._theme.styles:
            self._theme.styles[self._current_area] = Style()
        return self._theme.styles[self._current_area]

    # ── Bind input → model ────────────────────────────────────────────
    def on_input_changed(self, event: Input.Changed) -> None:
        s = self._current_style()
        wid = event.input.id or ""
        val = event.value or ""
        if wid == "fg" and is_valid_color(val):
            s.fg = normalize_color(val)
        elif wid == "bg" and is_valid_color(val):
            s.bg = normalize_color(val)
        elif wid == "font_size":
            try:
                s.font_size = max(6, min(48, int(val)))
            except ValueError:
                return
        else:
            return
        self._render_preview()

    def on_select_changed(self, event: Select.Changed) -> None:
        s = self._current_style()
        if event.select.id == "font_family":
            s.font_family = str(event.value)
        elif event.select.id == "align":
            s.align = str(event.value)
        else:
            return
        self._render_preview()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        s = self._current_style()
        wid = event.checkbox.id or ""
        if wid in {"bold", "italic", "underline", "blink", "marquee"}:
            setattr(s, wid, bool(event.value))
            self._render_preview()

    # ── Preview ────────────────────────────────────────────────────────
    def _render_preview(self) -> None:
        try:
            self.query_one("#preview", Static).update(
                render_preview_into_rich(self._theme)
            )
        except Exception:
            pass

    # ── Toolbar actions ────────────────────────────────────────────────
    async def action_about(self) -> None:
        await self.push_screen(AboutModal())

    async def action_preview_modal(self) -> None:
        await self.push_screen(_PreviewModal(self._theme))

    async def action_load_theme(self) -> None:
        opts = [(f"{t.name}  (built-in)" if t.name in BUILTIN_THEMES else t.name,
                 t.name) for t in list_themes()]
        choice = await self.push_screen_wait(_ChoiceModal("Load theme", opts))
        if not choice:
            return
        try:
            t = load_theme(choice)
        except FileNotFoundError as exc:
            self.notify(str(exc), severity="error", timeout=4)
            return
        new = Theme.from_dict(t.to_dict())
        new.name = "untitled"
        new.based_on = choice
        new.builtin = False
        self._theme = new
        self._render_editor(self._current_area)
        self._render_preview()
        self._refresh_hero()
        self.notify(f"Loaded '{choice}' as starting point.", timeout=3)

    async def action_save_as(self) -> None:
        proposed = self._theme.name if self._theme.name != "untitled" else "my-theme"
        new_name = await self.push_screen_wait(
            _PromptModal("Save theme as (name):", initial=proposed)
        )
        if not new_name:
            return
        if not is_valid_name(new_name):
            self.notify("Invalid theme name (letters / digits / spaces / -_ only).",
                         severity="error", timeout=4)
            return
        if new_name in BUILTIN_THEMES:
            self.notify(f"'{new_name}' is built-in — pick a different name.",
                         severity="error", timeout=4)
            return
        self._theme.name = new_name
        self._theme.builtin = False
        try:
            path = save_theme(self._theme)
        except (ReadOnlyThemeError, ValueError) as exc:
            self.notify(str(exc), severity="error", timeout=4)
            return
        self._refresh_hero()
        self.notify(f"Saved → {path}", timeout=4)

    async def action_set_default(self) -> None:
        try:
            set_default_theme(self._theme.name)
        except FileNotFoundError as exc:
            self.notify(str(exc), severity="error", timeout=4)
            return
        self._refresh_hero()
        self.notify(f"'{self._theme.name}' is now the default.", timeout=3)

    # ── Helpers ────────────────────────────────────────────────────────
    def _refresh_hero(self) -> None:
        try:
            self.query_one("#hero", Static).update(
                f"[bold blue]Lynx Theme[/] v{__version__}    "
                f"[dim]Working theme:[/] [bold]{self._theme.name}[/]    "
                f"[dim]Based on:[/] [italic]{self._theme.based_on or '—'}[/]    "
                f"[dim]Default:[/] [bold]{get_default_theme_name() or 'none'}[/]"
            )
        except Exception:
            pass

    @staticmethod
    def _make_initial(name: Optional[str]) -> Theme:
        if name:
            try:
                t = load_theme(name)
                new = Theme.from_dict(t.to_dict())
                new.name = "untitled"
                new.based_on = name
                new.builtin = False
                return new
            except FileNotFoundError:
                pass
        base = BUILTIN_THEMES["lynx-mocha"]
        new = Theme.from_dict(base.to_dict())
        new.name = "untitled"
        new.based_on = base.name
        new.builtin = False
        return new


def run_tui(initial_theme: Optional[str] = None) -> int:
    app = LynxThemeApp(initial_theme=initial_theme)
    app.run()
    return 0
