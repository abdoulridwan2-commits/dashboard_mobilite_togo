import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_reseau_routier():
    data = get_data()
    regions = data["regions"]

    render_header()
    section_title("État du réseau par région")

    stacked = regions[["region", "part_bon_pct", "part_moyen_pct", "part_mauvais_pct", "part_travaux_pct"]].copy()
    fig = px.bar(
        stacked.melt(id_vars="region", var_name="etat", value_name="part"),
        x="region",
        y="part",
        color="etat",
        title="Répartition de l'état des routes par région",
        labels={"region": "Région", "part": "Part (%)", "etat": "État"},
        barmode="stack",
    )
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Tableau synthétique")
    st.dataframe(
        regions[["region", "routes_km", "etat_bon_km", "etat_moyen_km", "etat_mauvais_km", "etat_travaux_km", "part_bon_pct", "part_mauvais_pct"]]
        .sort_values("part_mauvais_pct", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
    )
