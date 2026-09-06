"""PaperMint - academic citation extraction.

Streamlit entry point. Run with::

    streamlit run app.py

This script does four things and nothing else: configure the page, configure
logging, inject the stylesheet, and hand control to the router. Every screen
lives in ``papermint/ui/pages`` and every unit of work lives in the domain
layer beneath ``papermint/``.
"""

from __future__ import annotations

import logging
import os

import streamlit as st

from papermint.config import APP_ICON, APP_NAME, APP_TAGLINE, APP_VERSION
from papermint.ui.html import render
from papermint.ui.icons import icon
from papermint.ui.navigation import build_navigation
from papermint.ui.styles import inject_custom_css
from papermint.ui.theme import DEFAULT_MODE, PALETTES


def _configure_logging() -> None:
    """Configure application logging once per process.

    Without this the domain layer's ``logger.error`` and ``logger.exception``
    calls are discarded, which makes a production failure invisible. The level
    is read from ``PAPERMINT_LOG_LEVEL`` and defaults to INFO.
    """
    if logging.getLogger("papermint").handlers:
        return

    level = os.getenv("PAPERMINT_LOG_LEVEL", "INFO").upper()
    resolved = getattr(logging, level, logging.INFO)
    logging.basicConfig(
        level=resolved,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )
    logging.getLogger("papermint").setLevel(resolved)


def _render_sidebar_brand() -> None:
    """Render the wordmark and tagline at the top of the sidebar."""
    with st.sidebar:
        render(
            '<div class="pm-brand">'
            '<div class="pm-brand-row">'
            f'<span class="pm-brand-mark">{icon("leaf", size=18)}</span>'
            f'<span class="pm-brand-name">{APP_NAME}</span>'
            "</div>"
            f'<div class="pm-brand-tag">{APP_TAGLINE}</div>'
            "</div>"
        )


#: Which palette the reader has chosen. A widget owns this key, so the choice
#: survives a page switch the same way every other widget value does.
_THEME_KEY = "pm_theme_mode"

#: The palettes offered in Settings, with the label each one shows.
_THEME_CHOICES: dict[str, str] = {
    "dark": ":material/dark_mode: Dark",
    "light": ":material/light_mode: Light",
}


def _current_mode() -> str:
    """Return the palette to render in.

    Read before the stylesheet is injected, so the value a click just wrote is
    the one that paints this run. An unrecognised value falls back rather than
    raising: a stale session must not take the page down.

    Returns:
        ``"dark"`` or ``"light"``.
    """
    mode = st.session_state.get(_THEME_KEY)
    return mode if mode in PALETTES else DEFAULT_MODE


def _render_sidebar_settings() -> None:
    """Render the appearance control at the foot of the sidebar.

    Streamlit reruns the whole script on every interaction, so a click here
    writes the new mode into session state and the next run injects the other
    palette. Every rule in the stylesheet is written against a token, so one
    swapped ``:root`` block repaints the whole interface, and the crossfade on
    ``--pm-motion-theme`` carries it across rather than flashing.
    """
    with st.sidebar, st.expander("Settings", icon=":material/settings:"):
        st.caption("Appearance")
        st.pills(
            "Theme",
            options=list(_THEME_CHOICES),
            required=True,
            format_func=lambda mode: _THEME_CHOICES[mode],
            key=_THEME_KEY,
            label_visibility="collapsed",
        )


def main() -> None:
    """Configure the app and run the router."""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": f"{APP_NAME} {APP_VERSION} - academic citation extraction.",
        },
    )

    _configure_logging()
    st.session_state.setdefault(_THEME_KEY, DEFAULT_MODE)
    inject_custom_css(_current_mode())
    _render_sidebar_brand()

    navigation = build_navigation()
    st.sidebar.divider()
    _render_sidebar_settings()
    st.sidebar.caption(f"Version {APP_VERSION}")
    navigation.run()


main()
