import plotly.express as px
import streamlit as st

from utils.components import metric_card, render_header
from utils.data import get_data


def show_overview():
    data = get_data()
    vehicules = data["vehicules"]
    accidents = data["accidents"]
    regions = data["regions"]
    auto_ecoles = data["auto_ecoles"]

    render_header()

    latest_year = int(vehicules["annee"].max())
    latest_total = int(vehicules.loc[vehicules["annee"] == latest_year, "valeur"].sum())
    accidents_2022 = accidents.loc[accidents["annee"] == 2022].iloc[0]
    mauvais_km = regions["etat_mauvais_km"].sum()
    etat_total_km = regions["etat_total_km"].sum()
    part_mauvais_ponderee = mauvais_km / etat_total_km * 100
    immats_2022 = vehicules.loc[vehicules["annee"] == latest_year].groupby("groupe")["valeur"].sum()
    part_motos = immats_2022.get("Deux-roues", 0) / latest_total * 100
    worst_share = regions.sort_values("part_mauvais_pct", ascending=False).iloc[0]
    worst_absolute = regions.sort_values("etat_mauvais_km", ascending=False).iloc[0]

    st.markdown("<div class='kicker'>Vue d'ensemble</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        metric_card("Immatriculations annuelles", f"{latest_total:,.0f}", f"en {latest_year}, toutes catégories")
    with cols[1]:
        metric_card("Accidents", f"{int(accidents_2022['accidents']):,}", "en 2022, national")
    with cols[2]:
        metric_card("Routes en mauvais état", f"{part_mauvais_ponderee:.1f}%", "part pondérée, état 2020")
    with cols[3]:
        metric_card("Auto-écoles listées", f"{len(auto_ecoles):,}", "inventaire sans millésime dans le fichier")

    st.caption(
        "Les immatriculations sont un flux annuel, pas un parc roulant. Les accidents sont nationaux; "
        "l’état des routes est observé en 2020 (routes non attribuées exclues des parts) et "
        "l’inventaire des auto-écoles n’est pas daté."
    )

    min_year = int(vehicules["annee"].min())
    year_range = st.slider(
        "Période des immatriculations",
        min_value=min_year,
        max_value=latest_year,
        value=(min_year, latest_year),
        key="overview_vehicle_year_range",
    )
    groups = sorted(vehicules["groupe"].dropna().unique().tolist())
    selected_groups = st.multiselect(
        "Catégories affichées",
        groups,
        default=groups,
        key="overview_vehicle_groups",
    )
    chart_data = vehicules[
        vehicules["annee"].between(*year_range)
        & vehicules["groupe"].isin(selected_groups)
    ]
    if chart_data.empty:
        st.info("Sélectionne au moins une catégorie.")
    else:
        fig = px.line(
            chart_data,
            x="annee",
            y="valeur",
            color="groupe",
            markers=True,
            title="Flux annuel d’immatriculations par groupe",
            labels={"annee": "Année", "valeur": "Immatriculations", "groupe": "Groupe"},
        )
        fig.update_layout(template="plotly_white", legend_title_text="Groupe")
        st.plotly_chart(fig, width="stretch")

    st.markdown("### Constats mesurés")
    col1, col2 = st.columns(2)
    with col1:
        st.write(
            f"En {latest_year}, les deux-roues représentent {part_motos:.1f}% des immatriculations "
            "annuelles enregistrées. Cette part décrit le flux de l’année, pas la composition du parc en circulation."
        )
        st.write(
            f"En 2022, {int(accidents_2022['accidents']):,} accidents, "
            f"{int(accidents_2022['blesses']):,} blessés et {int(accidents_2022['morts']):,} morts "
            "sont enregistrés au niveau national. Les fichiers ne permettent pas une attribution territoriale."
        )

    with col2:
        st.write(
            f"Sur l’état routier 2020, {worst_share['region']} a la part la plus élevée de kilomètres "
            f"en mauvais état ({worst_share['part_mauvais_pct']:.1f}%), tandis que {worst_absolute['region']} "
            f"enregistre le plus grand volume ({worst_absolute['etat_mauvais_km']:.1f} km). "
            "Part et volume répondent à deux questions différentes."
        )
        maritime = auto_ecoles.loc[auto_ecoles["region"] == "Maritime"]
        st.write(
            f"L’inventaire contient {len(maritime)} entrées en Maritime sur {len(auto_ecoles)} au total. "
            "Le fichier n’indique pas sa date ni son exhaustivité; cela ne prouve pas l’absence de services ailleurs."
        )