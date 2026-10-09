import streamlit as st

from utils.components import render_header


def show_objectifs():
    render_header()
    st.markdown(
        """
        ### Objectifs

        - Décrire les immatriculations annuelles et les permis délivrés par catégorie.
        - Suivre séparément les accidents, les blessés et les morts.
        - Comparer l’état du réseau routier par longueur et proportion.
        - Explorer les géométries des routes classées et les points d’auto-écoles disponibles.
        - Formuler des pistes d’action reliées aux indicateurs et à leurs limites.
        """
    )

    st.markdown("### Périmètre des données")
    st.markdown(
        """
        - Immatriculations nationales : 1990-2022; les valeurs décrivent un flux annuel, pas le stock roulant.
        - Permis nationaux : 2007-2022; aucune valeur par catégorie en 2013.
        - Accidents, blessés et morts : série nationale 2010-2022, sans géographie ni type d’usager.
        - État des routes : un seul millésime, 2020; certaines longueurs sont attribuées manuellement ou non attribuées.
        - Population : recensement 2022; les populations antérieures ne sont pas disponibles dans les fichiers.
        - Auto-écoles : points géolocalisés, mais le fichier ne donne ni millésime ni preuve d’exhaustivité.
        """
    )

    st.markdown("### Limites d’interprétation")
    st.write(
        "Une variation observée ne démontre pas une cause. Les données ne permettent pas de relier "
        "les accidents à une région, à l’état d’un tronçon ou au type de véhicule. Les absences de "
        "l’inventaire cartographique sont signalées comme absence d’entrée, pas comme absence réelle de service."
    )
