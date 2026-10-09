import plotly.express as px
import streamlit as st

from utils.components import metric_card, render_header
from utils.data import get_data


def show_overview():
    data = get_data()
    vehicules = data["vehicules"]
    accidents = data["accidents"]
    regions = data["regions"]

    render_header("ADMINISTRATION TERRITORIALE ET MOBILITE | DEFI 1")

    latest_year = int(vehicules["annee"].max())
    latest_total = int(vehicules[vehicules["annee"] == latest_year]["valeur"].sum())
    accidents_2022 = accidents[accidents["annee"] == 2022].iloc[0]
    mauvais_etat = regions["part_mauvais_pct"].mean()

    st.markdown("<div class='kicker'>Vue d'ensemble</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[0]:
        metric_card("Véhicules immatriculés", f"{latest_total:,.0f}", f"en {latest_year}")
    with cols[1]:
        metric_card("Accidents", f"{int(accidents_2022['accidents']):,}", "en 2022")
    with cols[2]:
        metric_card("Réseau en mauvais état", f"{mauvais_etat:.1f}%", "part moyenne régionale")

    view_mode = st.radio("Visualisation", ["Graphique", "Carte"], horizontal=True, key="overview_mode")

    if view_mode == "Graphique":
        fig = px.line(
            vehicules[vehicules["groupe"].isin(["Deux-roues", "Voitures et camionnettes", "Poids lourds"])],
            x="annee",
            y="valeur",
            color="groupe",
            title="Évolution des véhicules immatriculés",
            labels={"annee": "Année", "valeur": "Nombre de véhicules", "groupe": "Catégorie"},
        )
        fig.update_layout(template="plotly_white", legend_title_text="Catégorie")
        st.plotly_chart(fig, use_container_width=True)
    else:
        map_data = regions.sort_values("auto_ecoles_pour_100k_hab", ascending=False)
        fig = px.bar(
            map_data,
            x="region",
            y="auto_ecoles_pour_100k_hab",
            title="Auto-écoles pour 100 000 habitants par région",
            color="region",
            labels={"region": "Région", "auto_ecoles_pour_100k_hab": "Auto-écoles / 100k hab"},
        )
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Analyse synthétique")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            - Les motos dominent aujourd’hui le parc de véhicules et expliquent la forte hausse des immatriculations.
            - Les accidents restent très élevés, avec plus de 7 500 cas enregistrés en 2022.
            - Le réseau routier est inégalement réparti : plusieurs régions affichent une part significative de tronçons en mauvais état.
            """
        )

    with col2:
        worst_region = regions.sort_values("part_mauvais_pct", ascending=False).iloc[0]
        best_region = regions.sort_values("part_bon_pct", ascending=False).iloc[0]
        st.markdown(
            f"""
            - La région la plus touchée par le mauvais état est **{worst_region['region']}** avec {worst_region['part_mauvais_pct']}% de routes en mauvais état.
            - La région la mieux servie est **{best_region['region']}** avec {best_region['part_bon_pct']}% de routes en bon état.
            - Les auto-écoles restent concentrées dans les zones urbaines, surtout dans la région Maritime.
            """
        )
