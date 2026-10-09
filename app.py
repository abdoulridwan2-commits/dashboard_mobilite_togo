import streamlit as st

from config import NAV_ITEMS
from utils.components import render_footer, render_sidebar
from views.accidents import show_accidents
from views.auto_ecoles import show_auto_ecoles
from views.cartographie import show_cartographie
from views.objectifs import show_objectifs
from views.overview import show_overview
from views.recommandations import show_recommandations
from views.reseau_routier import show_reseau_routier
from views.vehicukes_permis import show_vehicules_permis
from utils.style import inject_styles


st.set_page_config(
    page_title="Mobilité et sécurité routière au Togo",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

PAGES = {
    "Objectifs": show_objectifs,
    "Vue d'ensemble": show_overview,
    "Mobilité": show_vehicules_permis,
    "Sécurité routière": show_accidents,
    "Réseau routier": show_reseau_routier,
    "Cartographie": show_cartographie,
    "Auto-écoles": show_auto_ecoles,
    "Recommandations": show_recommandations,
}

selection = render_sidebar(NAV_ITEMS)

if selection in PAGES:
    PAGES[selection]()

render_footer()
