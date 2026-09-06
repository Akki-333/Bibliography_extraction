"""Design tokens for the PaperMint interface.

One source of truth for colour, type, spacing and elevation, consumed both by
the stylesheet and by the Python that picks a colour for a confidence band.
Hard-coded hex values elsewhere in ``papermint/ui`` are a defect: the token
should be added here instead.

The palette follows the design blueprint: mint on deep slate, with the
surfaces layered so that a card, a panel and the page background are
distinguishable without any border at all.
"""

from __future__ import annotations

from typing import Final

from papermint.models import ConfidenceBand

# ---------------------------------------------------------------------------
# Colour
# ---------------------------------------------------------------------------

#: Brand and semantic colours.
COLOR: Final[dict[str, str]] = {
    # Brand
    "accent": "#34D399",
    "accent-bright": "#6EE7B7",
    "accent-deep": "#10B981",
    "accent-ink": "#052E20",
    # Surfaces, from furthest back to closest to the reader.
    "canvas": "#0F172A",
    "surface": "#161F33",
    "surface-raised": "#1D293D",
    "surface-sunken": "#0B1120",
    # Lines
    "border": "#27354C",
    "border-strong": "#3A4B66",
    # Type
    "text": "#EEF2F8",
    "text-muted": "#9DACC2",
    "text-faint": "#6B7C96",
    # Status
    "positive": "#34D399",
    "caution": "#FBBF24",
    "critical": "#F87171",
    "info": "#60A5FA",
}

#: Translucent fills, used for chips and hover states.
ALPHA: Final[dict[str, str]] = {
    # A fully transparent accent, needed as the resting end of a pulsing ring:
    # animating to `transparent` fades through grey in some engines, animating
    # to the same hue at zero alpha does not.
    "accent-00": "rgba(52, 211, 153, 0)",
    "accent-08": "rgba(52, 211, 153, 0.08)",
    "accent-14": "rgba(52, 211, 153, 0.14)",
    "accent-24": "rgba(52, 211, 153, 0.24)",
    "caution-12": "rgba(251, 191, 36, 0.12)",
    "caution-28": "rgba(251, 191, 36, 0.28)",
    "critical-12": "rgba(248, 113, 113, 0.12)",
    "critical-28": "rgba(248, 113, 113, 0.28)",
    "info-12": "rgba(96, 165, 250, 0.12)",
    "shadow": "rgba(3, 7, 18, 0.45)",
}

#: The light palette. Same roles, same names, so every rule written against a
#: token keeps working; only the values invert. The accent darkens because mint
#: at #34D399 on white fails contrast for text, while the same hue at #059669
#: passes and still reads as the same brand.
LIGHT_COLOR: Final[dict[str, str]] = {
    # Deeper than the dark theme's mint, which washes out to nothing on white.
    # #047857 clears 4.5:1 on every surface here, so the accent can carry text
    # and not just decoration.
    "accent": "#047857",
    "accent-bright": "#065F46",
    "accent-deep": "#10B981",
    "accent-ink": "#FFFFFF",
    # Three real steps. The canvas is tinted so a white card lifts off it
    # without needing a heavy border, and the sunken step is darker than the
    # canvas so the sidebar reads as a distinct plane rather than a margin.
    "canvas": "#EEF2F8",
    "surface": "#FFFFFF",
    "surface-raised": "#FFFFFF",
    "surface-sunken": "#E2E8F1",
    # Borders that are actually visible. The old #DDE4EE vanished against a
    # near-white canvas, which is half of why the theme looked washed out.
    "border": "#BAC7DA",
    "border-strong": "#94A3B8",
    # A real hierarchy: 16:1, 8:1 and 5:1 against white. The old muted step sat
    # too close to the faint one, so nothing looked deliberate.
    "text": "#0B1220",
    "text-muted": "#3E4C61",
    "text-faint": "#5A6779",
    # Saturated enough to read as status at chip size, dark enough to pass
    # contrast as text on their own tints.
    "positive": "#047857",
    "caution": "#96540A",
    "critical": "#C81E1E",
    "info": "#1D4ED8",
}

#: Translucent fills for the light palette. Tints are stronger than their dark
#: counterparts because a wash that reads clearly on slate disappears on white.
LIGHT_ALPHA: Final[dict[str, str]] = {
    "accent-00": "rgba(4, 120, 87, 0)",
    "accent-08": "rgba(4, 120, 87, 0.07)",
    "accent-14": "rgba(4, 120, 87, 0.12)",
    "accent-24": "rgba(4, 120, 87, 0.28)",
    "caution-12": "rgba(150, 84, 10, 0.11)",
    "caution-28": "rgba(150, 84, 10, 0.30)",
    "critical-12": "rgba(200, 30, 30, 0.10)",
    "critical-28": "rgba(200, 30, 30, 0.28)",
    "info-12": "rgba(29, 78, 216, 0.10)",
    # Cool and soft. A light theme gets its depth from shadow, where a dark one
    # gets it from a lighter surface, so this carries more weight here.
    "shadow": "rgba(15, 23, 42, 0.10)",
}

#: The two palettes by name. ``mode`` travels as a plain string so that session
#: state, the stylesheet and the toggle all speak the same language.
PALETTES: Final[dict[str, tuple[dict[str, str], dict[str, str]]]] = {
    "dark": (COLOR, ALPHA),
    "light": (LIGHT_COLOR, LIGHT_ALPHA),
}

#: The mode used when nothing has chosen one.
DEFAULT_MODE: Final[str] = "dark"

#: The palette token each confidence band points at.
#:
#: A card writes ``--pm-band`` into its own style attribute, so if that carried
#: a literal hex the card would be painted in whichever palette happened to be
#: loaded when the module was imported. It carries a ``var()`` reference
#: instead, which the current ``:root`` resolves - the card is themed by the
#: stylesheet like everything else, and section 9's rule that colour lives only
#: here holds even for markup built at render time.
BAND_TOKEN: Final[dict[ConfidenceBand, str]] = {
    ConfidenceBand.HIGH: "--pm-color-positive",
    ConfidenceBand.MEDIUM: "--pm-color-caution",
    ConfidenceBand.LOW: "--pm-color-critical",
}

#: The translucent fill token matching each confidence band.
BAND_FILL_TOKEN: Final[dict[ConfidenceBand, str]] = {
    ConfidenceBand.HIGH: "--pm-fill-accent-14",
    ConfidenceBand.MEDIUM: "--pm-fill-caution-12",
    ConfidenceBand.LOW: "--pm-fill-critical-12",
}


def band_color(band: ConfidenceBand) -> str:
    """Return the accent colour for a confidence band.

    Args:
        band: The confidence band.

    Returns:
        A CSS ``var()`` reference, resolved against whichever palette is
        loaded.
    """
    return f"var({BAND_TOKEN.get(band, '--pm-color-text-faint')})"


def band_fill(band: ConfidenceBand) -> str:
    """Return the translucent fill for a confidence band.

    Args:
        band: The confidence band.

    Returns:
        A CSS ``var()`` reference, resolved against whichever palette is
        loaded.
    """
    return f"var({BAND_FILL_TOKEN.get(band, '--pm-fill-info-12')})"


# ---------------------------------------------------------------------------
# Type
# ---------------------------------------------------------------------------

#: Font stacks. A serif carries bibliographic content so that titles and
#: prose read as scholarly text rather than as interface chrome.
FONT: Final[dict[str, str]] = {
    "ui": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "text": "'Source Serif 4', 'Iowan Old Style', Georgia, serif",
    "mono": "'JetBrains Mono', 'SF Mono', ui-monospace, Menlo, monospace",
}

#: Modular type scale, in rem against a 16px root.
TYPE_SCALE: Final[dict[str, str]] = {
    "micro": "0.6875rem",  # 11px — eyebrow labels
    "xs": "0.75rem",  # 12px — chips, captions
    "sm": "0.8125rem",  # 13px — metadata
    "base": "0.875rem",  # 14px — body
    "md": "1rem",  # 16px — lead paragraphs
    "lg": "1.125rem",  # 18px — card titles
    "xl": "1.375rem",  # 22px — section headings
    "2xl": "1.75rem",  # 28px — page titles
    "3xl": "2.25rem",  # 36px — hero
}

# ---------------------------------------------------------------------------
# Space, shape and motion
# ---------------------------------------------------------------------------

#: Spacing scale in pixels. Every margin and padding uses a step from here.
SPACE: Final[dict[str, str]] = {
    "1": "4px",
    "2": "8px",
    "3": "12px",
    "4": "16px",
    "5": "20px",
    "6": "24px",
    "8": "32px",
    "10": "40px",
    "12": "48px",
    "16": "64px",
}

#: Corner radii.
RADIUS: Final[dict[str, str]] = {
    "sm": "6px",
    "md": "10px",
    "lg": "14px",
    "pill": "999px",
}

#: Two elevation levels only; more reads as noise on a dark ground.
SHADOW: Final[dict[str, str]] = {
    "raised": f"0 1px 2px {ALPHA['shadow']}",
    "floating": f"0 12px 32px -8px {ALPHA['shadow']}",
}

#: Shared easing and duration.
#:
#: ``fast`` and ``base`` are interface feedback: a hover, a focus ring, a
#: border warming up. ``enter`` and ``reveal`` are content arriving, and they
#: use a decelerating curve that overshoots nothing, so a list of citations
#: settles onto the page rather than sliding in like a carousel. ``stagger`` is
#: the delay step between neighbouring items in a revealed sequence: below
#: about 40ms the cascade reads as one flicker, above about 90ms the last item
#: feels late.
MOTION: Final[dict[str, str]] = {
    "fast": "120ms cubic-bezier(0.4, 0, 0.2, 1)",
    "base": "200ms cubic-bezier(0.4, 0, 0.2, 1)",
    "enter": "460ms cubic-bezier(0.16, 1, 0.3, 1)",
    "reveal": "620ms cubic-bezier(0.16, 1, 0.3, 1)",
    "stagger": "55ms",
    # The palette crossfade. Slower than interface feedback because the
    # whole page changes at once and a fast swap reads as a flash.
    "theme": "320ms cubic-bezier(0.4, 0, 0.2, 1)",
}


def css_variables(mode: str = DEFAULT_MODE) -> str:
    """Render one palette's tokens as a CSS custom property block.

    Args:
        mode: ``"dark"`` or ``"light"``. An unknown mode falls back to the
            default rather than raising, because this runs on every render and
            a bad session value must not take the page down.

    Returns:
        The contents of a ``:root { ... }`` declaration, without the selector.
    """
    colours, alphas = PALETTES.get(mode, PALETTES[DEFAULT_MODE])

    lines: list[str] = []
    for name, value in colours.items():
        lines.append(f"--pm-color-{name}: {value};")
    for name, value in alphas.items():
        lines.append(f"--pm-fill-{name}: {value};")
    for name, value in FONT.items():
        lines.append(f"--pm-font-{name}: {value};")
    for name, value in TYPE_SCALE.items():
        lines.append(f"--pm-text-{name}: {value};")
    for name, value in SPACE.items():
        lines.append(f"--pm-space-{name}: {value};")
    for name, value in RADIUS.items():
        lines.append(f"--pm-radius-{name}: {value};")
    for name, value in SHADOW.items():
        lines.append(f"--pm-shadow-{name}: {value};")
    for name, value in MOTION.items():
        lines.append(f"--pm-motion-{name}: {value};")
    return "\n".join(f"    {line}" for line in lines)


__all__ = [
    "ALPHA",
    "BAND_FILL_TOKEN",
    "BAND_TOKEN",
    "COLOR",
    "DEFAULT_MODE",
    "FONT",
    "LIGHT_ALPHA",
    "LIGHT_COLOR",
    "MOTION",
    "PALETTES",
    "RADIUS",
    "SHADOW",
    "SPACE",
    "TYPE_SCALE",
    "band_color",
    "band_fill",
    "css_variables",
]
