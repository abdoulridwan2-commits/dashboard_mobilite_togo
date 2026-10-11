import base64
from html import escape
from pathlib import Path

import streamlit as st

from config import APP_SUBTITLE, APP_TITLE, COLORS


def render_header(title: str = APP_TITLE, subtitle: str = APP_SUBTITLE):
    """Affiche le bandeau institutionnel vert en haut de page."""
    st.markdown(
        f"""
        <div class="top-banner">
            <div class="banner-decor-left"></div>
            <div class="banner-copy">
                <span class="banner-badge">TOGO AI LAB · DATA CHALLENGES</span>
                <h1 class="banner-title">{escape(title)}</h1>
                <p class="banner-subtitle">{escape(subtitle)}</p>
                <div class="banner-accent-bar"></div>
            </div>
            <div class="banner-decor-right"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: str = "", icon: str = "", help_text: str = ""):
    """Affiche une carte métrique moderne avec étiquette, valeur, delta et icône."""
    icon_html = f'<span class="metric-icon">{icon}</span>' if icon else ""
    help_html = f'<div class="metric-help">{escape(help_text)}</div>' if help_text else ""
    delta_html = f'<div class="metric-detail">{escape(delta)}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-header">
                <div class="metric-label">{escape(label)}</div>
                {icon_html}
            </div>
            <div class="metric-value">{escape(value)}</div>
            {delta_html}
            {help_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(items):
    """Affiche la barre latérale avec le logo, la navigation, le bouton reset et la phrase de conclusion."""
    emblem_path = Path(__file__).resolve().parent.parent / "assets" / "Armoiries_du_Togo.svg"
    emblem_b64 = ""
    if emblem_path.exists():
        emblem_b64 = base64.b64encode(emblem_path.read_bytes()).decode("ascii")

    st.sidebar.markdown(
        f"""
        <div class="sidebar-logo">
            <img class="sidebar-emblem" src="data:image/svg+xml;base64,{emblem_b64}" alt="Armoiries du Togo">
            <div class="sidebar-brand">
                <div class="name">Togo AI Lab</div>
                <div class="subname">Data Challenges 2024</div>
                <div class="sidebar-attribution">
                    <a href="https://commons.wikimedia.org/wiki/File:Armoiries_du_Togo.svg" target="_blank">Armoiries · CC BY-SA 4.0</a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<div class='sidebar-nav-title'>NAVIGATION</div>", unsafe_allow_html=True)
    selection = st.sidebar.radio("Navigation", items, index=0, label_visibility="collapsed", key="main_nav_radio")

    def _reset_all_filters():
        st.session_state["filter_version"] = st.session_state.get("filter_version", 0) + 1

    st.sidebar.markdown("<div class='nav-reset-holder'>", unsafe_allow_html=True)
    st.sidebar.button("🔄 Réinitialiser les filtres", on_click=_reset_all_filters, use_container_width=True, key="btn_global_reset")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)



    # Phrase demandée en bas de la barre latérale
    st.sidebar.markdown(
        """
        <div class="sidebar-quote-box">
            <div class="quote-flag-bar"></div>
            <p class="quote-text">« Des routes plus sûres, une mobilité durable pour le Togo »</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selection


def render_footer():
    """Affiche le pied de page officiel."""
    st.markdown(
        """
        <div class="footer-note">
            Dashboard réalisé par <strong>Abdoulaye Ridwan</strong> · Défi 1 : Administration territoriale et mobilité (Togo AI Lab)
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, subtitle: str = ""):
    """Affiche un titre de section soigné."""
    sub_html = f"<div class='section-subtitle'>{escape(subtitle)}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class='section-header'>
            <div class='section-title'>{escape(title)}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def data_limitation_box(text: str, title: str = "Périmètre et limites méthodologiques"):
    """Encadré d'avertissement méthodologique."""
    st.markdown(
        f"""
        <div class="limitation-box">
            <div class="limitation-title">ℹ️ {escape(title)}</div>
            <div class="limitation-text">{escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

