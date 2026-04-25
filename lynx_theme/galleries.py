"""Curated galleries of icons, colour palettes, and font samples.

These are exposed to the GUI/TUI editor so users can pick from a rich
catalog of pre-built choices instead of typing Unicode codepoints or hex
codes by hand. Every gallery is a plain Python data structure so it can
also be consumed by tests, the TUI, and external tooling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Icon gallery
# ---------------------------------------------------------------------------

@dataclass
class IconEntry:
    glyph: str
    name: str
    keywords: Tuple[str, ...] = field(default_factory=tuple)


# Curated, themed catalogues of pure-Unicode glyphs (emoji + symbols) that
# render in any modern terminal/Tk widget without external font files.
ICON_GALLERY: Dict[str, List[IconEntry]] = {
    "Finance & Markets": [
        IconEntry("📈", "trend up", ("growth", "bull", "rise")),
        IconEntry("📉", "trend down", ("loss", "bear", "fall")),
        IconEntry("📊", "bar chart", ("dashboard", "stats")),
        IconEntry("💹", "yen chart up", ("forex", "fx", "asia")),
        IconEntry("💰", "money bag", ("cash", "savings")),
        IconEntry("💵", "dollar bill", ("usd", "money")),
        IconEntry("💴", "yen bill", ("jpy", "money")),
        IconEntry("💶", "euro bill", ("eur", "money")),
        IconEntry("💷", "pound bill", ("gbp", "money")),
        IconEntry("🪙", "coin", ("crypto", "metal")),
        IconEntry("💳", "credit card", ("payment", "spend")),
        IconEntry("🏦", "bank", ("vault", "deposit")),
        IconEntry("🏛", "classical building", ("treasury", "central bank")),
        IconEntry("📅", "calendar", ("date", "schedule", "earnings")),
        IconEntry("⏰", "alarm", ("alert", "deadline")),
        IconEntry("⏳", "hourglass flow", ("pending", "wait")),
        IconEntry("🔒", "lock", ("escrow", "secure")),
        IconEntry("🔓", "unlock", ("released", "open")),
        IconEntry("📦", "package", ("etf basket", "holding")),
        IconEntry("🧾", "receipt", ("invoice", "tax")),
        IconEntry("💎", "diamond", ("hold", "long-term")),
        IconEntry("🐂", "bull", ("bull market",)),
        IconEntry("🐻", "bear", ("bear market",)),
    ],
    "Status & Verdict": [
        IconEntry("✓", "check", ("ok", "pass", "success")),
        IconEntry("✘", "cross", ("fail", "error", "no")),
        IconEntry("⚠", "warning", ("caution", "yellow")),
        IconEntry("ⓘ", "info circle", ("note",)),
        IconEntry("❓", "question", ("unknown",)),
        IconEntry("❗", "exclamation", ("alert",)),
        IconEntry("🚫", "prohibited", ("avoid", "blocked")),
        IconEntry("⛔", "no entry", ("stop",)),
        IconEntry("✅", "green check", ("done",)),
        IconEntry("❌", "red x", ("rejected",)),
        IconEntry("🟢", "green dot", ("buy", "positive")),
        IconEntry("🟡", "yellow dot", ("hold", "neutral")),
        IconEntry("🔴", "red dot", ("sell", "risk")),
        IconEntry("🔵", "blue dot", ("info", "neutral")),
        IconEntry("⚪", "white dot", ("muted",)),
        IconEntry("⚫", "black dot", ("muted",)),
        IconEntry("🟣", "purple dot", ("agent",)),
        IconEntry("🟠", "orange dot", ("warning", "tier-micro")),
        IconEntry("⭐", "star", ("favorite", "default")),
        IconEntry("🏆", "trophy", ("winner", "top pick")),
        IconEntry("🥇", "gold medal", ("first",)),
        IconEntry("🥈", "silver medal", ("second",)),
        IconEntry("🥉", "bronze medal", ("third",)),
    ],
    "Navigation & Actions": [
        IconEntry("📥", "inbox", ("load", "import")),
        IconEntry("📤", "outbox", ("export",)),
        IconEntry("💾", "floppy", ("save",)),
        IconEntry("📂", "folder open", ("load", "browse")),
        IconEntry("📁", "folder", ("directory",)),
        IconEntry("🔍", "magnifier", ("search", "find")),
        IconEntry("🔎", "magnifier right", ("search",)),
        IconEntry("🗑", "trash", ("delete", "remove")),
        IconEntry("✏", "pencil", ("edit",)),
        IconEntry("📝", "memo", ("notes",)),
        IconEntry("🖨", "printer", ("print",)),
        IconEntry("🔄", "refresh cycle", ("reload",)),
        IconEntry("🔃", "refresh down-up", ("sync",)),
        IconEntry("↩", "return", ("back",)),
        IconEntry("↪", "forward", ("redo",)),
        IconEntry("⏮", "skip back", ("first",)),
        IconEntry("⏭", "skip forward", ("last",)),
        IconEntry("⏯", "play/pause", ("toggle",)),
        IconEntry("⏸", "pause", ("hold",)),
        IconEntry("▶", "play", ("run", "go")),
        IconEntry("⏹", "stop", ("halt",)),
        IconEntry("➕", "plus", ("add",)),
        IconEntry("➖", "minus", ("remove",)),
        IconEntry("✕", "small x", ("close",)),
        IconEntry("⚙", "gear", ("settings",)),
        IconEntry("🔧", "wrench", ("config",)),
        IconEntry("🔨", "hammer", ("build",)),
    ],
    "Communication & Docs": [
        IconEntry("📧", "email", ("mail", "contact")),
        IconEntry("📨", "incoming envelope", ("inbox",)),
        IconEntry("📬", "mailbox", ("inbox",)),
        IconEntry("📞", "phone", ("call",)),
        IconEntry("📡", "satellite", ("feed",)),
        IconEntry("📰", "newspaper", ("news", "article")),
        IconEntry("📜", "scroll", ("doc", "license")),
        IconEntry("📄", "document", ("file", "page")),
        IconEntry("📃", "page curl", ("doc",)),
        IconEntry("📑", "tabs", ("bookmarks",)),
        IconEntry("🔖", "bookmark", ("favorite",)),
        IconEntry("📚", "books", ("library",)),
        IconEntry("📖", "open book", ("reading",)),
        IconEntry("📘", "blue book", ("manual",)),
        IconEntry("📙", "orange book", ("guide",)),
        IconEntry("📕", "red book", ("alert doc",)),
        IconEntry("📗", "green book", ("approved doc",)),
    ],
    "Data & Analytics": [
        IconEntry("🧮", "abacus", ("calculate",)),
        IconEntry("📐", "ruler", ("measure",)),
        IconEntry("📏", "straight ruler", ("scale",)),
        IconEntry("🧪", "test tube", ("experiment", "analysis")),
        IconEntry("🔬", "microscope", ("research",)),
        IconEntry("🧬", "dna", ("genome", "deep")),
        IconEntry("🗂", "card index", ("archive",)),
        IconEntry("🗃", "file box", ("archive",)),
        IconEntry("🗄", "filing cabinet", ("storage",)),
        IconEntry("📋", "clipboard", ("checklist",)),
        IconEntry("🖥", "desktop", ("workstation",)),
        IconEntry("💻", "laptop", ("dev",)),
        IconEntry("⌨", "keyboard", ("input",)),
        IconEntry("🖱", "mouse", ("input",)),
        IconEntry("🤖", "robot", ("agent", "ai")),
        IconEntry("🧠", "brain", ("ai", "thought")),
        IconEntry("🛰", "satellite", ("signal", "feed")),
    ],
    "World & Languages": [
        IconEntry("🌐", "globe meridians", ("world", "international")),
        IconEntry("🌍", "globe europe-africa", ("emea",)),
        IconEntry("🌎", "globe americas", ("us", "latam")),
        IconEntry("🌏", "globe asia-australia", ("apac",)),
        IconEntry("🗺", "world map", ("geo",)),
        IconEntry("🇺🇸", "flag US", ("us", "english")),
        IconEntry("🇪🇸", "flag ES", ("spain", "spanish")),
        IconEntry("🇮🇹", "flag IT", ("italy", "italian")),
        IconEntry("🇩🇪", "flag DE", ("germany", "german")),
        IconEntry("🇫🇷", "flag FR", ("france", "french")),
        IconEntry("🇮🇷", "flag IR", ("iran", "farsi")),
        IconEntry("🇬🇧", "flag GB", ("uk",)),
        IconEntry("🇯🇵", "flag JP", ("japan",)),
        IconEntry("🇨🇳", "flag CN", ("china",)),
        IconEntry("🇧🇷", "flag BR", ("brazil",)),
    ],
    "Sectors & Industry": [
        IconEntry("⚡", "bolt", ("energy", "electric")),
        IconEntry("🔋", "battery", ("energy storage",)),
        IconEntry("☢", "radioactive", ("nuclear",)),
        IconEntry("🛢", "oil drum", ("oil", "energy")),
        IconEntry("🌱", "seedling", ("esg", "growth")),
        IconEntry("🌿", "herb", ("esg", "green")),
        IconEntry("🏭", "factory", ("industrials",)),
        IconEntry("🏗", "construction", ("infra",)),
        IconEntry("🏠", "house", ("real estate",)),
        IconEntry("🏢", "office", ("reit", "corporate")),
        IconEntry("🏬", "department store", ("retail", "consumer")),
        IconEntry("🚗", "car", ("autos",)),
        IconEntry("✈", "plane", ("airlines", "travel")),
        IconEntry("🚢", "ship", ("shipping",)),
        IconEntry("🛒", "cart", ("retail",)),
        IconEntry("🍎", "apple", ("consumer", "food")),
        IconEntry("☕", "coffee", ("consumer",)),
        IconEntry("🩺", "stethoscope", ("healthcare",)),
        IconEntry("💊", "pill", ("pharma",)),
        IconEntry("🧬", "dna", ("biotech",)),
        IconEntry("📱", "phone", ("tech",)),
        IconEntry("🎮", "controller", ("gaming",)),
        IconEntry("🎬", "clapper", ("media",)),
    ],
    "Symbols & Misc": [
        IconEntry("♥", "heart", ("favorite",)),
        IconEntry("♠", "spade", ("card",)),
        IconEntry("♦", "diamond suit", ("card",)),
        IconEntry("♣", "club", ("card",)),
        IconEntry("♻", "recycle", ("loop", "esg")),
        IconEntry("⚖", "balance", ("legal", "compare")),
        IconEntry("⚓", "anchor", ("stable",)),
        IconEntry("⌘", "command", ("shortcut",)),
        IconEntry("⏱", "stopwatch", ("benchmark",)),
        IconEntry("⏲", "timer", ("countdown",)),
        IconEntry("☀", "sun", ("light",)),
        IconEntry("☁", "cloud", ("backup",)),
        IconEntry("☂", "umbrella", ("hedge",)),
        IconEntry("☔", "umbrella with rain", ("protection",)),
        IconEntry("☘", "shamrock", ("luck",)),
        IconEntry("☄", "comet", ("burst",)),
        IconEntry("⚛", "atom", ("science",)),
        IconEntry("∞", "infinity", ("forever",)),
        IconEntry("∑", "sigma", ("sum",)),
        IconEntry("π", "pi", ("constant",)),
        IconEntry("∫", "integral", ("calculus",)),
        IconEntry("≈", "almost equal", ("approx",)),
        IconEntry("≠", "not equal", ("diff",)),
        IconEntry("≤", "less or equal", ("bound",)),
        IconEntry("≥", "greater or equal", ("bound",)),
    ],
}


def all_icons() -> List[IconEntry]:
    """Flatten the gallery into one list (preserves category order)."""
    out: List[IconEntry] = []
    for entries in ICON_GALLERY.values():
        out.extend(entries)
    return out


def search_icons(query: str) -> List[IconEntry]:
    """Case-insensitive substring search across name + keywords + glyph."""
    q = (query or "").strip().lower()
    if not q:
        return all_icons()
    hits: List[IconEntry] = []
    for entry in all_icons():
        haystack = " ".join((entry.name, entry.glyph, *entry.keywords)).lower()
        if q in haystack:
            hits.append(entry)
    return hits


# ---------------------------------------------------------------------------
# Colour palettes
# ---------------------------------------------------------------------------

@dataclass
class ColorSwatch:
    name: str
    hex: str


# Curated palettes — every one of these is also useful for theming the
# real Suite. Hex codes lower-case, no shorthand.
COLOR_PALETTES: Dict[str, List[ColorSwatch]] = {
    "Catppuccin Mocha": [
        ColorSwatch("Rosewater", "#f5e0dc"),
        ColorSwatch("Flamingo",  "#f2cdcd"),
        ColorSwatch("Pink",      "#f5c2e7"),
        ColorSwatch("Mauve",     "#cba6f7"),
        ColorSwatch("Red",       "#f38ba8"),
        ColorSwatch("Maroon",    "#eba0ac"),
        ColorSwatch("Peach",     "#fab387"),
        ColorSwatch("Yellow",    "#f9e2af"),
        ColorSwatch("Green",     "#a6e3a1"),
        ColorSwatch("Teal",      "#94e2d5"),
        ColorSwatch("Sky",       "#89dceb"),
        ColorSwatch("Sapphire",  "#74c7ec"),
        ColorSwatch("Blue",      "#89b4fa"),
        ColorSwatch("Lavender",  "#b4befe"),
        ColorSwatch("Text",      "#cdd6f4"),
        ColorSwatch("Subtext1",  "#bac2de"),
        ColorSwatch("Subtext0",  "#a6adc8"),
        ColorSwatch("Overlay2",  "#9399b2"),
        ColorSwatch("Overlay1",  "#7f849c"),
        ColorSwatch("Overlay0",  "#6c7086"),
        ColorSwatch("Surface2",  "#585b70"),
        ColorSwatch("Surface1",  "#45475a"),
        ColorSwatch("Surface0",  "#313244"),
        ColorSwatch("Base",      "#1e1e2e"),
        ColorSwatch("Mantle",    "#181825"),
        ColorSwatch("Crust",     "#11111b"),
    ],
    "Catppuccin Latte": [
        ColorSwatch("Rosewater", "#dc8a78"),
        ColorSwatch("Flamingo",  "#dd7878"),
        ColorSwatch("Pink",      "#ea76cb"),
        ColorSwatch("Mauve",     "#8839ef"),
        ColorSwatch("Red",       "#d20f39"),
        ColorSwatch("Maroon",    "#e64553"),
        ColorSwatch("Peach",     "#fe640b"),
        ColorSwatch("Yellow",    "#df8e1d"),
        ColorSwatch("Green",     "#40a02b"),
        ColorSwatch("Teal",      "#179299"),
        ColorSwatch("Sky",       "#04a5e5"),
        ColorSwatch("Sapphire",  "#209fb5"),
        ColorSwatch("Blue",      "#1e66f5"),
        ColorSwatch("Lavender",  "#7287fd"),
        ColorSwatch("Text",      "#4c4f69"),
        ColorSwatch("Subtext1",  "#5c5f77"),
        ColorSwatch("Subtext0",  "#6c6f85"),
        ColorSwatch("Overlay2",  "#7c7f93"),
        ColorSwatch("Overlay1",  "#8c8fa1"),
        ColorSwatch("Overlay0",  "#9ca0b0"),
        ColorSwatch("Surface2",  "#acb0be"),
        ColorSwatch("Surface1",  "#bcc0cc"),
        ColorSwatch("Surface0",  "#ccd0da"),
        ColorSwatch("Base",      "#eff1f5"),
        ColorSwatch("Mantle",    "#e6e9ef"),
        ColorSwatch("Crust",     "#dce0e8"),
    ],
    "Material Design": [
        ColorSwatch("Red 500",       "#f44336"),
        ColorSwatch("Pink 500",      "#e91e63"),
        ColorSwatch("Purple 500",    "#9c27b0"),
        ColorSwatch("Deep Purple",   "#673ab7"),
        ColorSwatch("Indigo 500",    "#3f51b5"),
        ColorSwatch("Blue 500",      "#2196f3"),
        ColorSwatch("Light Blue",    "#03a9f4"),
        ColorSwatch("Cyan 500",      "#00bcd4"),
        ColorSwatch("Teal 500",      "#009688"),
        ColorSwatch("Green 500",     "#4caf50"),
        ColorSwatch("Light Green",   "#8bc34a"),
        ColorSwatch("Lime 500",      "#cddc39"),
        ColorSwatch("Yellow 500",    "#ffeb3b"),
        ColorSwatch("Amber 500",     "#ffc107"),
        ColorSwatch("Orange 500",    "#ff9800"),
        ColorSwatch("Deep Orange",   "#ff5722"),
        ColorSwatch("Brown 500",     "#795548"),
        ColorSwatch("Grey 500",      "#9e9e9e"),
        ColorSwatch("Blue Grey",     "#607d8b"),
        ColorSwatch("Black",         "#000000"),
        ColorSwatch("White",         "#ffffff"),
    ],
    "Tailwind CSS": [
        ColorSwatch("slate-500",   "#64748b"),
        ColorSwatch("gray-500",    "#6b7280"),
        ColorSwatch("zinc-500",    "#71717a"),
        ColorSwatch("red-500",     "#ef4444"),
        ColorSwatch("orange-500",  "#f97316"),
        ColorSwatch("amber-500",   "#f59e0b"),
        ColorSwatch("yellow-500",  "#eab308"),
        ColorSwatch("lime-500",    "#84cc16"),
        ColorSwatch("green-500",   "#22c55e"),
        ColorSwatch("emerald-500", "#10b981"),
        ColorSwatch("teal-500",    "#14b8a6"),
        ColorSwatch("cyan-500",    "#06b6d4"),
        ColorSwatch("sky-500",     "#0ea5e9"),
        ColorSwatch("blue-500",    "#3b82f6"),
        ColorSwatch("indigo-500",  "#6366f1"),
        ColorSwatch("violet-500",  "#8b5cf6"),
        ColorSwatch("purple-500",  "#a855f7"),
        ColorSwatch("fuchsia-500", "#d946ef"),
        ColorSwatch("pink-500",    "#ec4899"),
        ColorSwatch("rose-500",    "#f43f5e"),
    ],
    "Solarized": [
        ColorSwatch("base03",  "#002b36"),
        ColorSwatch("base02",  "#073642"),
        ColorSwatch("base01",  "#586e75"),
        ColorSwatch("base00",  "#657b83"),
        ColorSwatch("base0",   "#839496"),
        ColorSwatch("base1",   "#93a1a1"),
        ColorSwatch("base2",   "#eee8d5"),
        ColorSwatch("base3",   "#fdf6e3"),
        ColorSwatch("yellow",  "#b58900"),
        ColorSwatch("orange",  "#cb4b16"),
        ColorSwatch("red",     "#dc322f"),
        ColorSwatch("magenta", "#d33682"),
        ColorSwatch("violet",  "#6c71c4"),
        ColorSwatch("blue",    "#268bd2"),
        ColorSwatch("cyan",    "#2aa198"),
        ColorSwatch("green",   "#859900"),
    ],
    "Dracula": [
        ColorSwatch("Background", "#282a36"),
        ColorSwatch("Current Line","#44475a"),
        ColorSwatch("Foreground", "#f8f8f2"),
        ColorSwatch("Comment",    "#6272a4"),
        ColorSwatch("Cyan",       "#8be9fd"),
        ColorSwatch("Green",      "#50fa7b"),
        ColorSwatch("Orange",     "#ffb86c"),
        ColorSwatch("Pink",       "#ff79c6"),
        ColorSwatch("Purple",     "#bd93f9"),
        ColorSwatch("Red",        "#ff5555"),
        ColorSwatch("Yellow",     "#f1fa8c"),
    ],
    "Nord": [
        ColorSwatch("Polar 0",  "#2e3440"),
        ColorSwatch("Polar 1",  "#3b4252"),
        ColorSwatch("Polar 2",  "#434c5e"),
        ColorSwatch("Polar 3",  "#4c566a"),
        ColorSwatch("Snow 0",   "#d8dee9"),
        ColorSwatch("Snow 1",   "#e5e9f0"),
        ColorSwatch("Snow 2",   "#eceff4"),
        ColorSwatch("Frost 0",  "#8fbcbb"),
        ColorSwatch("Frost 1",  "#88c0d0"),
        ColorSwatch("Frost 2",  "#81a1c1"),
        ColorSwatch("Frost 3",  "#5e81ac"),
        ColorSwatch("Aurora R", "#bf616a"),
        ColorSwatch("Aurora O", "#d08770"),
        ColorSwatch("Aurora Y", "#ebcb8b"),
        ColorSwatch("Aurora G", "#a3be8c"),
        ColorSwatch("Aurora P", "#b48ead"),
    ],
    "Gruvbox Dark": [
        ColorSwatch("bg",       "#282828"),
        ColorSwatch("bg1",      "#3c3836"),
        ColorSwatch("bg2",      "#504945"),
        ColorSwatch("bg3",      "#665c54"),
        ColorSwatch("fg",       "#ebdbb2"),
        ColorSwatch("fg1",      "#d5c4a1"),
        ColorSwatch("red",      "#cc241d"),
        ColorSwatch("green",    "#98971a"),
        ColorSwatch("yellow",   "#d79921"),
        ColorSwatch("blue",     "#458588"),
        ColorSwatch("purple",   "#b16286"),
        ColorSwatch("aqua",     "#689d6a"),
        ColorSwatch("orange",   "#d65d0e"),
        ColorSwatch("gray",     "#928374"),
    ],
    "Suite Accents": [
        ColorSwatch("Mocha bg",   "#1e1e2e"),
        ColorSwatch("Mocha card", "#2a2a3d"),
        ColorSwatch("Lynx blue",  "#89b4fa"),
        ColorSwatch("Lynx cyan",  "#74c7ec"),
        ColorSwatch("Lynx mauve", "#cba6f7"),
        ColorSwatch("Lynx green", "#a6e3a1"),
        ColorSwatch("Lynx yellow","#f9e2af"),
        ColorSwatch("Lynx red",   "#f38ba8"),
        ColorSwatch("Lynx peach", "#fab387"),
        ColorSwatch("Lynx text",  "#cdd6f4"),
        ColorSwatch("Lynx muted", "#6c7086"),
        ColorSwatch("Lynx border","#45475a"),
    ],
}


def all_palettes() -> List[str]:
    return list(COLOR_PALETTES.keys())


def palette(name: str) -> List[ColorSwatch]:
    return list(COLOR_PALETTES.get(name, ()))


# ---------------------------------------------------------------------------
# Font sample helpers
# ---------------------------------------------------------------------------

# A short sentence + numerals that exercises ascenders, descenders, and
# digits — useful for comparing fonts at a glance.
FONT_SAMPLE_SENTENCE = (
    "Lince Investor Suite — Vanguard 500 Index $1.42T  |  "
    "AaBbCc 0123456789  ▲▼ ✓ ✘ €¥£"
)


PREFERRED_FONT_FAMILIES: Tuple[str, ...] = (
    "Noto Sans",
    "Noto Sans Mono",
    "DejaVu Sans",
    "DejaVu Sans Mono",
    "Liberation Sans",
    "Liberation Mono",
    "Liberation Serif",
    "Helvetica",
    "Arial",
    "Segoe UI",
    "Consolas",
    "Courier New",
    "Menlo",
    "Monaco",
    "Times New Roman",
    "Georgia",
    "Fira Code",
    "Fira Sans",
    "JetBrains Mono",
    "Source Sans 3",
    "Source Code Pro",
    "Roboto",
    "Roboto Mono",
    "Cantarell",
    "Ubuntu",
    "Ubuntu Mono",
    "Inter",
    "Lato",
    "Open Sans",
)


def order_fonts(available: List[str]) -> List[str]:
    """Return *available* with PREFERRED families surfaced first."""
    avail = list(available)
    head = [f for f in PREFERRED_FONT_FAMILIES if f in avail]
    seen = set(head)
    tail = [f for f in avail if f not in seen]
    return head + tail
