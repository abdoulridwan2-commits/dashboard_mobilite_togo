import streamlit as st

from utils.components import render_header


def show_objectifs():
    render_header("Objectifs du dashboard")
    st.markdown(
        """
        ### Objectifs

        - Retracer l’évolution des véhicules immatriculés et des permis délivrés par catégorie.
        - Mesurer la sécurité routière à partir des accidents, blessés et morts.
        - Évaluer l’état du réseau routier par région et par tronçon.
        - Cartographier le réseau classé et la densité des auto-écoles.
        - Formuler des recommandations ciblées pour renforcer la sécurité et la mobilité.
        """
    )

    st.markdown("### Points de vigilance")
    st.write(
        "Le parc est dominé par les deux-roues, ce qui multiplie les risques de collision et rend la sécurité routière plus sensible à la qualité de la formation et à l’entretien du réseau."
    )
