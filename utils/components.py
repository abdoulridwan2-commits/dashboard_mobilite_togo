import base64
from pathlib import Path

import streamlit as st

from config import APP_TITLE, COLORS


def render_header(title: str = APP_TITLE):
    st.markdown(
        f"""
        <div class="top-banner">
            <div class="banner-left">
                <div class="logo-mark">🛵</div>
            </div>
            <div class="banner-title">{title}</div>
            <div class="banner-right">
                <div class="banner-photo"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-detail">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(items):
    emblem_path = Path(__file__).resolve().parent.parent / "assets" / "Armoiries_du_Togo.svg"
    emblem = base64.b64encode(emblem_path.read_bytes()).decode("ascii")
    st.sidebar.markdown(
        f"""
        <div class="sidebar-logo">
            <img class="sidebar-emblem" src="data:image/svg+xml;base64,{emblem}" alt="Armoiries du Togo">
            <div class="sidebar-brand">
                <div class="name">Togo AI Lab</div>
                <div class="sidebar-attribution">
                    <a href="https://commons.wikimedia.org/wiki/File:Armoiries_du_Togo.svg" target="_blank">Edem Fiadjoe · Wikimedia Commons</a><br>
                    <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">CC BY-SA 4.0</a>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selection = st.sidebar.radio("Navigation", items, index=0, label_visibility="collapsed")

    st.sidebar.markdown("<div class='nav-reset-holder'>", unsafe_allow_html=True)
    if st.sidebar.button("◌ Réinitialiser", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    return selection


def render_footer():
    st.markdown(
        """
        <div class="footer-note">Dashboard réalisé par Abdoulaye Ridwan</div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
