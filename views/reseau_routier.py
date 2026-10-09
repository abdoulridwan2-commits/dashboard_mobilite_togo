import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_reseau_routier():
    data = get_data()
    etat_routes = data["etat_routes"]

    render_header()
    section_title("État du réseau routier, millésime 2020")
    st.caption(
        "La source décrit les routes revêtues et en terre en 2020; elle ne permet pas une évolution "
        "dans le temps. Les voiries urbaines sont séparées car elles ne sont pas régionalisées."
    )

    network_types = ["Toutes"] + sorted(
        etat_routes.loc[etat_routes["type_reseau"].str.startswith("Routes"), "type_reseau"].unique().tolist()
    )
    network_type = st.selectbox("Catégorie de réseau", network_types, key="road_state_type")
    region_options = ["Toutes"] + sorted(
        etat_routes.loc[
            etat_routes["type_reseau"].str.startswith("Routes")
            & ~etat_routes["region"].isin(["Non attribué", "Voiries (non régionalisées)"]),
            "region",
        ].dropna().unique().tolist()
    )
    region = st.selectbox("Région", region_options, key="road_state_region")

    routes = etat_routes[etat_routes["type_reseau"].str.startswith("Routes")].copy()
    if network_type != "Toutes":
        routes = routes[routes["type_reseau"] == network_type]
    if region != "Toutes":
        routes = routes[routes["region"] == region]

    region_routes = routes[
        ~routes["region"].isin(["Non attribué", "Voiries (non régionalisées)"])
    ]
    state_columns = ["bon_km", "moyen_km", "mauvais_km", "travaux_km"]
    summary = region_routes.groupby("region")[state_columns].sum().reset_index()
    summary["total_connu_km"] = summary[state_columns].sum(axis=1)
    state_labels = {
        "bon_km": "Bon état",
        "moyen_km": "État moyen",
        "mauvais_km": "Mauvais état",
        "travaux_km": "Travaux en cours",
    }
    for column in state_columns:
        summary[f"{column}_pct"] = summary[column] / summary["total_connu_km"] * 100

    if summary.empty:
        st.info("Aucune donnée d’état attribuée à ce filtre.")
    else:
        total_known = summary["total_connu_km"].sum()
        bad_km = summary["mauvais_km"].sum()
        works_km = summary["travaux_km"].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Longueur d’état recensée", f"{total_known:,.1f} km")
        col2.metric("Mauvais état", f"{bad_km:,.1f} km", f"{bad_km / total_known * 100:.1f}% du total affiché")
        col3.metric("Travaux en cours", f"{works_km:,.1f} km")

        share_data = summary.melt(
            id_vars="region",
            value_vars=[f"{column}_pct" for column in state_columns],
            var_name="etat",
            value_name="part_pct",
        )
        share_data["etat"] = share_data["etat"].str.removesuffix("_pct").map(state_labels)
        fig = px.bar(
            share_data,
            x="region",
            y="part_pct",
            color="etat",
            title="Répartition en pourcentage par région",
            labels={"region": "Région", "part_pct": "Part des km (%)", "etat": "État"},
            barmode="stack",
            category_orders={"etat": list(state_labels.values())},
        )
        fig.update_layout(template="plotly_white", yaxis_range=[0, 100])
        st.plotly_chart(fig, width="stretch")

        length_data = summary[["region"] + state_columns].melt(
            id_vars="region", var_name="etat", value_name="longueur_km"
        )
        length_data["etat"] = length_data["etat"].map(state_labels)
        fig_lengths = px.bar(
            length_data,
            x="region",
            y="longueur_km",
            color="etat",
            title="Longueur absolue par état",
            labels={"region": "Région", "longueur_km": "Longueur (km)", "etat": "État"},
            barmode="stack",
            category_orders={"etat": list(state_labels.values())},
        )
        fig_lengths.update_layout(template="plotly_white")
        st.plotly_chart(fig_lengths, width="stretch")

        table = summary[["region"] + state_columns + ["total_connu_km"]].rename(
            columns={**state_labels, "total_connu_km": "total_connu_km"}
        )
        st.dataframe(table.round(1), width="stretch", hide_index=True)

        st.markdown("#### Détail par tronçon")
        detail_columns = [
            "troncon", "type_reseau", "region", "source_region",
            "bon_km", "moyen_km", "mauvais_km", "travaux_km",
            "travaux_enregistrement_source_present", "total_km",
        ]
        details = routes[detail_columns].sort_values("mauvais_km", ascending=False).rename(
            columns={
                "troncon": "Tronçon",
                "type_reseau": "Catégorie",
                "region": "Région attribuée",
                "source_region": "Méthode d’attribution",
                "bon_km": "Bon état (km)",
                "moyen_km": "État moyen (km)",
                "mauvais_km": "Mauvais état (km)",
                "travaux_km": "Travaux listés (km)",
                "travaux_enregistrement_source_present": "Ligne TRAVAUX source présente",
                "total_km": "Total états (km)",
            }
        )
        st.dataframe(
            details,
            width="stretch",
            hide_index=True,
        )

        absent_work_rows = int((~routes["travaux_enregistrement_source_present"]).sum())
        if absent_work_rows:
            st.warning(
                f"Pour {absent_work_rows} tronçon(s) du filtre, la source ne contient pas de ligne TRAVAUX. "
                "Le 0 affiché signifie « aucune valeur listée », pas une mesure explicite de zéro kilomètre."
            )

    all_classified_routes = etat_routes[etat_routes["type_reseau"].str.startswith("Routes")]
    unassigned_km = all_classified_routes.loc[
        all_classified_routes["region"] == "Non attribué", "total_km"
    ].sum()
    manual_km = all_classified_routes.loc[
        all_classified_routes["source_region"].str.startswith("manuel"), "total_km"
    ].sum()
    st.warning(
        f"Limites d’attribution : {manual_km:.1f} km ont une région attribuée manuellement; "
        f"{unassigned_km:.1f} km restent non attribués et sont exclus des parts régionales."
    )
    st.caption(
        "Priorisation descriptive seulement : le volume en mauvais état et sa proportion ne tiennent "
        "pas compte du trafic, de la population desservie, de la gravité des accidents ni du coût des travaux."
    )
