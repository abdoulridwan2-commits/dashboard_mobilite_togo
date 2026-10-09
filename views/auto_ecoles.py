import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_auto_ecoles():
    data = get_data()
    auto_ecoles = data["auto_ecoles"]
    pref = data["prefectures"]

    render_header()
    section_title("Répartition géographique et densité")

    par_region = auto_ecoles.groupby("region").size().reset_index(name="nb_auto_ecoles")
    fig = px.bar(
        par_region,
        x="region",
        y="nb_auto_ecoles",
        title="Nombre d’auto-écoles par région",
        color="region",
        labels={"region": "Région", "nb_auto_ecoles": "Nombre d’auto-écoles"},
    )
    fig.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        pref[["prefecture", "region", "auto_ecoles", "auto_ecoles_pour_100k_hab"]].sort_values("auto_ecoles_pour_100k_hab", ascending=False),
        use_container_width=True,
    )
