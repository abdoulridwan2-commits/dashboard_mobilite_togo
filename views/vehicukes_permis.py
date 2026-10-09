import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_vehicules_permis():
    data = get_data()
    vehicules = data["vehicules"]
    permis = data["permis"]

    render_header("ADMINISTRATION TERRITORIALE ET MOBILITE | DEFI 1")
    section_title("Évolution du parc et des titres de conduite")

    fig1 = px.line(
        vehicules,
        x="annee",
        y="valeur",
        color="groupe",
        title="Parc de véhicules immatriculés par catégorie",
        labels={"annee": "Année", "valeur": "Nombre", "groupe": "Catégorie"},
    )
    fig1.update_layout(template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        permis[permis["annee"] == 2022],
        x="libelle",
        y="valeur",
        color="libelle",
        title="Permis délivrés en 2022 par catégorie",
        labels={"libelle": "Catégorie", "valeur": "Nombre de permis"},
    )
    fig2.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Points clés")
    st.write(
        "- Les deux-roues sont le moteur principal de la croissance du parc.\n"
        "- Les motos restent la catégorie la plus représentée et continuent d'accroître le volume de trafic.\n"
        "- Les permis de conduire légers restent dominants, mais la sécurisation des conducteurs de deux-roues mérite une attention spécifique."
    )
