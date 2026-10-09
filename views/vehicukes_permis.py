import pandas as pd
import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_vehicules_permis():
    data = get_data()
    vehicules = data["vehicules"]
    permis = data["permis"]

    render_header()
    section_title("Évolution des immatriculations et des permis")
    st.caption(
        "Données nationales. Les immatriculations sont un flux annuel, pas le parc roulant. "
        "La période commune aux deux séries est 2007-2022."
    )

    year_range = st.slider(
        "Période affichée",
        min_value=2007,
        max_value=2022,
        value=(2007, 2022),
        key="vehicules_permis_year_range",
    )
    groups = sorted(vehicules["groupe"].dropna().unique().tolist())
    selected_groups = st.multiselect(
        "Catégories de véhicules",
        groups,
        default=groups,
        key="vehicules_permis_groups",
    )
    categories = sorted(permis["libelle"].dropna().unique().tolist())
    selected_categories = st.multiselect(
        "Catégories de permis",
        categories,
        default=categories,
        key="vehicules_permis_categories",
    )

    vehicle_data = vehicules[
        vehicules["annee"].between(*year_range)
        & vehicules["groupe"].isin(selected_groups)
    ]
    permit_data = permis[
        permis["annee"].between(*year_range)
        & permis["libelle"].isin(selected_categories)
    ]

    left, right = st.columns(2)
    with left:
        st.markdown("#### Immatriculations annuelles")
        if vehicle_data.empty:
            st.info("Sélectionne au moins une catégorie de véhicules.")
        else:
            fig_vehicles = px.line(
                vehicle_data,
                x="annee",
                y="valeur",
                color="groupe",
                markers=True,
                labels={"annee": "Année", "valeur": "Immatriculations", "groupe": "Groupe"},
            )
            fig_vehicles.update_traces(connectgaps=False)
            fig_vehicles.update_layout(template="plotly_white", legend_title_text="Groupe")
            st.plotly_chart(fig_vehicles, width="stretch")

    with right:
        st.markdown("#### Permis délivrés par catégorie")
        if permit_data.empty:
            st.info("Sélectionne au moins une catégorie de permis.")
        else:
            fig_permits = px.line(
                permit_data,
                x="annee",
                y="valeur",
                color="libelle",
                markers=True,
                labels={"annee": "Année", "valeur": "Permis délivrés", "libelle": "Catégorie"},
            )
            fig_permits.update_traces(connectgaps=False)
            fig_permits.update_layout(template="plotly_white", legend_title_text="Catégorie")
            st.plotly_chart(fig_permits, width="stretch")

    missing_years = sorted(
        int(year)
        for year, values in permis.groupby("annee")["valeur"]
        if values.isna().all()
    )
    if missing_years:
        st.warning(
            f"Permis : aucune valeur par catégorie en {', '.join(map(str, missing_years))}. "
            "Ces années restent manquantes et ne sont pas assimilées à zéro."
        )

    st.markdown("#### Comparaison des évolutions (indice base 100)")
    st.caption(
        "L’indice compare les variations, pas les volumes : 100 correspond à la première année "
        "commune renseignée dans la période. Il ne démontre pas de lien causal."
    )
    vehicle_group = st.selectbox(
        "Groupe de véhicules",
        groups,
        key="comparison_vehicle_group",
    )
    permit_category = st.selectbox(
        "Catégorie de permis",
        categories,
        key="comparison_permit_category",
    )

    vehicle_series = (
        vehicules.loc[vehicules["groupe"] == vehicle_group]
        .groupby("annee")["valeur"]
        .sum()
        .rename("Immatriculations annuelles")
    )
    permit_series = (
        permis.loc[permis["libelle"] == permit_category]
        .set_index("annee")["valeur"]
        .rename("Permis délivrés")
    )
    comparison = pd.concat([vehicle_series, permit_series], axis=1).loc[
        year_range[0] : year_range[1]
    ]
    common_years = comparison.dropna()
    if common_years.empty:
        st.info("Aucune année commune renseignée dans la période sélectionnée.")
    else:
        base_year = int(common_years.index.min())
        indexed = comparison.div(common_years.loc[base_year]).mul(100)
        indexed.index.name = "annee"
        indexed = indexed.reset_index().melt(
            id_vars="annee", var_name="série", value_name="Indice base 100"
        )
        fig_index = px.line(
            indexed,
            x="annee",
            y="Indice base 100",
            color="série",
            markers=True,
            labels={"annee": "Année", "série": "Série"},
        )
        fig_index.update_traces(connectgaps=False)
        fig_index.update_layout(template="plotly_white", title=f"Base 100 en {base_year}")
        st.plotly_chart(fig_index, width="stretch")