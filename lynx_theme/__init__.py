"""Lynx Theme — visual theme editor for the Lince Investor Suite.

Lets users create, preview and save themes that drive the colour, font
and emphasis style of every Suite GUI and TUI application. The editor
itself is only available in **graphical** and **TUI** modes (the
console flow is reserved for read-only listing). Saved themes can be
loaded as the default on startup, exported to other users, or imported
into the Lynx Suite via :func:`lynx_theme.storage.register_user_themes`.
"""

from __future__ import annotations

__version__ = "6.0.0"
__author__ = "Borja Tarraso"
__author_email__ = "borja.tarraso@member.fsf.org"
__year__ = "2026"
__license__ = "BSD-3-Clause"

SUITE_NAME = "Lince Investor Suite"
SUITE_VERSION = "6.0.0"
SUITE_LABEL = f"{SUITE_NAME} v{SUITE_VERSION}"
APP_NAME = "Lynx Theme"


LICENSE_TEXT = """\
BSD 3-Clause License

Copyright (c) 2026, Borja Tarraso <borja.tarraso@member.fsf.org>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""


def get_logo_ascii() -> str:
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "img", "logo_ascii.txt")
    try:
        with open(p, "r") as f:
            return f.read().rstrip("\n")
    except OSError:
        return ""


def get_about_text() -> dict:
    return {
        "name": APP_NAME,
        "suite": SUITE_NAME,
        "suite_version": SUITE_VERSION,
        "suite_label": SUITE_LABEL,
        "version": __version__,
        "author": __author__,
        "email": __author_email__,
        "year": __year__,
        "license": __license__,
        "license_text": LICENSE_TEXT,
        "description": (
            "Visual theme editor for the Lince Investor Suite. Tune "
            "background, foreground, accent, headings, metric labels, "
            "warning / error / success colours, font face, font size, "
            "and bold / italic / underline / blink / marquee styling — "
            "with live preview. Save under any name and set as default.\n\n"
            "Available in graphical and TUI modes only."
        ),
    }
