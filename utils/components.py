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
    st.sidebar.markdown(
        """
        <div class="sidebar-logo">
            <div class="mark">🦁</div>
            <div class="name">Togo AI Lab</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("### Objectifs")
    selection = st.sidebar.radio("Navigation", items, index=1, label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Sections")

    st.sidebar.markdown("<div class='nav-box'>🚦 Mobilité</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='nav-box'>🛡️ Sécurité routière</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='nav-box'>🛣️ Réseau routier</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='nav-box'>🗺️ Cartographie</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='nav-box'>💡 Recommandations</div>", unsafe_allow_html=True)

    if st.sidebar.button("🔄 Réinitialiser", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]

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
