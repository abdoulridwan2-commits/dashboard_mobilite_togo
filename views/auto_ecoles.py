import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_auto_ecoles():
    data = get_data()
    auto_ecoles = data["auto_ecoles"]
    pref = data["prefectures"]

    render_header()
    section_title("Répartition des auto-écoles recensées")
    st.caption(
        "Les comptes sont des entrées du fichier géolocalisé (272 points); la source ne précise pas "
        "son millésime ni son exhaustivité. Les taux utilisent la population du recensement 2022 "
        "et restent descriptifs tant que la date de l’inventaire n’est pas connue."
    )

    regions = ["Toutes"] + sorted(pref["region"].dropna().unique().tolist())
    region = st.selectbox("Région", regions, key="auto_ecoles_region")
    filtered_pref = pref if region == "Toutes" else pref[pref["region"] == region]
    prefectures = ["Toutes"] + sorted(filtered_pref["prefecture"].dropna().unique().tolist())
    prefecture = st.selectbox("Préfecture", prefectures, key="auto_ecoles_prefecture")

    shown_pref = filtered_pref
    shown_schools = auto_ecoles
    if region != "Toutes":
        shown_schools = shown_schools[shown_schools["region"] == region]
    if prefecture != "Toutes":
        shown_pref = shown_pref[shown_pref["prefecture"] == prefecture]
        shown_schools = shown_schools[shown_schools["prefecture"] == prefecture]

    count_col, population_col = st.columns(2)
    with count_col:
        st.metric("Entrées d’auto-écoles listées", f"{len(shown_schools):,}")
    with population_col:
        if prefecture != "Toutes" and not shown_pref.empty:
            population = int(shown_pref.iloc[0]["population_2022"])
            st.metric("Population de référence", f"{population:,}", "recensement 2022")
        else:
            st.metric("Préfectures affichées", f"{shown_pref['prefecture'].nunique():,}")

    if prefecture != "Toutes" and not shown_pref.empty:
        row = shown_pref.iloc[0]
        if not bool(row["auto_ecoles_entree_presente"]):
            st.warning(
                "Aucune entrée d’auto-école n’est présente pour cette préfecture dans le fichier. "
                "Cela ne prouve pas qu’aucun service n’y existe."
            )
        else:
            rate = row["auto_ecoles_pour_100k_hab"]
            st.write(
                f"Entrées recensées : {int(row['auto_ecoles'])}; "
                f"ratio descriptif : {rate:.2f} pour 100 000 habitants (population 2022)."
            )

    by_region = shown_schools.groupby("region").size().reset_index(name="entrees_listees")
    if by_region.empty:
        st.info("Aucune entrée de l’inventaire ne correspond au filtre sélectionné.")
    else:
        fig = px.bar(
            by_region,
            x="region",
            y="entrees_listees",
            color="region",
            title="Entrées d’auto-écoles dans le fichier par région",
            labels={"region": "Région", "entrees_listees": "Entrées listées"},
        )
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, width="stretch")

    columns = ["prefecture", "region", "population_2022", "auto_ecoles",
               "auto_ecoles_entree_presente", "auto_ecoles_pour_100k_hab"]
    table = shown_pref[columns].rename(
        columns={
            "prefecture": "Préfecture",
            "region": "Région",
            "population_2022": "Population (2022)",
            "auto_ecoles": "Entrées listées",
            "auto_ecoles_entree_presente": "Ligne du registre présente",
            "auto_ecoles_pour_100k_hab": "Entrées / 100 000 hab. (descriptif)",
        }
    )
    st.dataframe(
        table.sort_values("Entrées listées", ascending=False),
        width="stretch",
        hide_index=True,
    )
