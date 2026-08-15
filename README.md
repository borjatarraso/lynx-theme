# Lynx Theme

Visual theme editor for the **Lince Investor Suite**. Tune every styled
area of every Suite app — window, panels, headings, metric labels and
values, listed instruments, warnings, errors, success rows, buttons, hero
banner — with live preview and font / size / bold / italic / underline /
blink / marquee controls.

Available in **graphical** and **TUI** mode only — by design, theme
editing requires live colour and font preview that the console cannot
deliver.

## Features

- Catppuccin-Mocha framed editor with the Suite logo.
- 15 customisable styled areas with end-user-friendly labels.
- Foreground / background colour pickers (click swatch or type hex).
- Font-family dropdown previewing each option in its own face.
- Font-size spinner, alignment dropdown, emphasis flags
  (bold / italic / underline / blink / marquee).
- Live preview pane that updates after every change, plus a free-floating
  preview window via `Ctrl+P`.
- Toolbar: Load (read-only when picking a built-in), Save As,
  Set as Default, Live Preview Window, About, Quit.
- TUI editor with Listed-area sidebar + per-area editor + live Rich
  preview at the bottom; `L` Load, `s` Save As, `d` Set Default, `p`
  Preview, `a` About, `g` Cycle language, `q` Quit.
- Persists themes to `$XDG_CONFIG_HOME/lynx-theme/themes/<name>.json`.
- Default-pointer file at `$XDG_CONFIG_HOME/lynx-theme/default.json` is
  read by every Suite app on startup.
- Three built-in **read-only** reference themes that ship with the
  package: `lynx-mocha`, `lynx-latte`, `lynx-high-contrast`. Loading a
  built-in always starts a fresh copy.

## Usage

```bash
lynx-theme              # → GUI editor (default)
lynx-theme -tui         # Textual editor
lynx-theme --list       # List built-in + user themes
lynx-theme --show NAME  # Print one theme as JSON
lynx-theme --preview NAME   # Render the demo styled by NAME
lynx-theme --set-default NAME
lynx-theme --about
```

## Languages

`lynx-theme` honours the Suite-wide `--language` flag (`us` / `es` / `it`
/ `de` / `fr` / `fa`) and persists the user's choice to
`$XDG_CONFIG_HOME/lynx/language.json`.

---

## Author and signature

This project is part of the **Lince Investor Suite**, authored and signed by

> **Borja Tarraso** &lt;[borja.tarraso@member.fsf.org](mailto:borja.tarraso@member.fsf.org)&gt;
> Licensed under BSD-3-Clause.

Every report and export emitted by Suite tools includes this same
signature in its footer. The shipped logo PNGs additionally carry the
author's signature via steganography for provenance — please do not
replace or re-encode the logo files.

<!-- LYNX-EP-FOOTER:BEGIN -->

---

## Entry point

New here, or coming back after a while? Read [`index.ep.md`](index.ep.md) (or open [`index.ep.html`](index.ep.html) in a browser) — the standard card that answers what this is, where to look first, and how to run it, in the same shape for every project.

🔴 **DORMANT** · last touched **28 April 2026**

## Ownership

<img src="https://www.cortex-university.com/static/brand/lince-logo.png" alt="Lince" width="96" height="96" align="left" style="margin-right:16px" />

**Lynx Theme is proudly part of Lince.**

| Company ID | Headquarters |
|---|---|
| 3015071-2 | Helsinki, Finland |

Part of the LINCE company · © All rights reserved

<!-- LYNX-EP-FOOTER:END -->
