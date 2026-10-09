import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_accidents():
    data = get_data()
    accidents = data["accidents"]

    render_header()
    section_title("Évolution des accidents, blessés et morts")

    fig = px.line(
        accidents,
        x="annee",
        y=["accidents", "blesses", "morts"],
        title="Accidents, blessés et morts entre 2010 et 2022",
        labels={"value": "Nombre", "variable": "Indicateur", "annee": "Année"},
    )
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Analyse de risque")
    col1, col2, col3 = st.columns(3)
    accident_2022 = accidents[accidents["annee"] == 2022].iloc[0]

    with col1:
        st.metric("Accidents / 1000 véhicules", f"{accident_2022['accidents_pour_1000_vehicules']:.2f}")
    with col2:
        st.metric("Morts / 100k habitants", f"{accident_2022['morts_pour_100k_hab']:.2f}")
    with col3:
        st.metric("Taux de gravité", f"{accident_2022['gravite_morts_pour_100_accidents']:.2f}%")

    st.markdown(
        """
        - Les accidents augmentent fortement au rythme du parc automobile, surtout avec la motorisation à deux roues.
        - Les blessés restent beaucoup plus nombreux que les morts, ce qui révèle une pression très forte sur les urgences et la prévention.
        - La mortalité est plus élevée dans les zones à faible couverture routière et à moindre formation des conducteurs.
        """
    )
