import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_cartographie():
    data = get_data()
    routes = data["routes"]
    auto_ecoles = data["auto_ecoles"]

    render_header("Cartographie")
    section_title("Réseau routier et distribution des auto-écoles")

    st.write("Répartition des auto-écoles par région et par préfecture :")
    regional_map = auto_ecoles.groupby(["region", "prefecture"]).size().reset_index(name="nb_auto_ecoles")
    st.dataframe(regional_map.sort_values("nb_auto_ecoles", ascending=False), use_container_width=True)

    if auto_ecoles[["latitude", "longitude"]].notna().all().all():
        st.map(auto_ecoles[["latitude", "longitude"]].dropna().reset_index(drop=True))

    st.markdown("### Données de référence")
    st.write(f"Le jeu de routes classées compte {len(routes)} segments, répartis par région et préfecture.")
    st.write("Les cartes permettent d’identifier les zones où l’offre de mobilité est faible et où le réseau a besoin d’investissement prioritaires.")
