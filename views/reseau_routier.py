import plotly.express as px
import streamlit as st

from config import COLORS
from utils.components import data_limitation_box, metric_card, render_header, section_title
from utils.data import get_data


def show_reseau_routier():
    data = get_data()
    etat_routes = data["etat_routes"]

    render_header()
    section_title("État du réseau routier (Millésime 2020)", "Diagnostic par région, tronçon et niveau de dégradation")

    # --- PANNEAU DE FILTRES ---
    v = st.session_state.get("filter_version", 0)
    with st.expander("🔍 Filtres d'affichage du réseau routier", expanded=False):
        col_f1, col_f2 = st.columns(2)

        cat_options = ["Toutes les routes"] + sorted(
            etat_routes.loc[etat_routes["type_reseau"].str.startswith("Routes"), "type_reseau"].unique().tolist()
        )
        with col_f1:
            cat_sel = st.selectbox("Catégorie de réseau", cat_options, key=f"rr_cat_{v}")

        reg_options = ["Toutes les régions"] + sorted(
            etat_routes.loc[
                etat_routes["type_reseau"].str.startswith("Routes")
                & ~etat_routes["region"].isin(["Non attribué", "Voiries (non régionalisées)"]),
                "region",
            ].dropna().unique().tolist()
        )
        with col_f2:
            reg_sel = st.selectbox("Région administrative", reg_options, key=f"rr_reg_{v}")



    # --- FILTRAGE DES DONNÉES ---
    routes = etat_routes[etat_routes["type_reseau"].str.startswith("Routes")].copy()
    if cat_sel != "Toutes les routes":
        routes = routes[routes["type_reseau"] == cat_sel]
    if reg_sel != "Toutes les régions":
        routes = routes[routes["region"] == reg_sel]

    # Données régionales valides pour l'agrégation
    routes_valides = routes[~routes["region"].isin(["Non attribué", "Voiries (non régionalisées)"])].copy()

    state_columns = ["bon_km", "moyen_km", "mauvais_km", "travaux_km"]
    summary = routes_valides.groupby("region")[state_columns].sum().reset_index()
    summary["total_km"] = summary[state_columns].sum(axis=1)

    state_labels = {
        "bon_km": "Bon état",
        "moyen_km": "État moyen",
        "mauvais_km": "Mauvais état",
        "travaux_km": "Travaux en cours",
    }
    for col in state_columns:
        summary[f"{col}_pct"] = (summary[col] / summary["total_km"] * 100).round(1)

    # --- CARTES KPI DU RÉSEAU ---
    k1, k2, k3, k4 = st.columns(4)
    tot_km = summary["total_km"].sum()
    bon_km = summary["bon_km"].sum()
    moyen_km = summary["moyen_km"].sum()
    mauvais_km = summary["mauvais_km"].sum()
    travaux_km = summary["travaux_km"].sum()

    with k1:
        metric_card(
            label="Linéaire analysé",
            value=f"{tot_km:,.1f} km".replace(",", " "),
            delta=f"{len(routes)} tronçons recensés",
            icon="🛣️",
        )
    with k2:
        part_bon = (bon_km / tot_km * 100) if tot_km > 0 else 0
        metric_card(
            label="Bon état",
            value=f"{bon_km:,.1f} km".replace(",", " "),
            delta=f"{part_bon:.1f}% du linéaire",
            icon="✅",
        )
    with k3:
        part_mauvais = (mauvais_km / tot_km * 100) if tot_km > 0 else 0
        metric_card(
            label="Mauvais état",
            value=f"{mauvais_km:,.1f} km".replace(",", " "),
            delta=f"⚠️ {part_mauvais:.1f}% à réhabiliter",
            icon="🚨",
        )
    with k4:
        metric_card(
            label="Chantiers & Travaux",
            value=f"{travaux_km:,.1f} km".replace(",", " "),
            delta="Travaux en cours en 2020",
            icon="🚧",
        )

    # --- DOUBLE PERSPECTIVE ANALYTIQUE : PART RELATIVE (%) VS VOLUME ABSOLU (KM) ---
    st.markdown("### 📊 La double grille d'analyse : Part relative (%) vs Volume kilométrique (km)")
    st.caption(
        "Une région peut avoir une forte proportion de dégradation sans avoir le plus grand linéaire en kilomètres. "
        "Les priorités d'investissement dépendent de cette distinction essentielle."
    )

    col_g, col_d = st.columns(2)

    color_dict = {
        "Bon état": COLORS["success"],
        "État moyen": COLORS["warning"],
        "Mauvais état": COLORS["danger"],
        "Travaux en cours": COLORS["purple"],
    }

    with col_g:
        st.markdown("#### 1. Structure relative par région (%)")
        if not summary.empty:
            share_data = summary.melt(
                id_vars="region",
                value_vars=[f"{c}_pct" for c in state_columns],
                var_name="etat_col",
                value_name="part_pct",
            )
            share_data["État"] = share_data["etat_col"].str.replace("_pct", "").map(state_labels)

            fig_p = px.bar(
                share_data,
                x="region",
                y="part_pct",
                color="État",
                barmode="stack",
                labels={"region": "Région", "part_pct": "Part des kilomètres (%)", "État": "État"},
                color_discrete_map=color_dict,
                category_orders={"État": list(state_labels.values())},
            )
            fig_p.update_layout(
                template="plotly_white",
                yaxis_range=[0, 100],
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_p, use_container_width=True)

    with col_d:
        st.markdown("#### 2. Longueur absolue par région (km)")
        if not summary.empty:
            len_data = summary.melt(
                id_vars="region",
                value_vars=state_columns,
                var_name="etat_col",
                value_name="km",
            )
            len_data["État"] = len_data["etat_col"].map(state_labels)

            fig_km = px.bar(
                len_data,
                x="region",
                y="km",
                color="État",
                barmode="stack",
                labels={"region": "Région", "km": "Longueur (km)", "État": "État"},
                color_discrete_map=color_dict,
                category_orders={"État": list(state_labels.values())},
            )
            fig_km.update_layout(
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_km, use_container_width=True)

    # --- TABLEAU DÉTAILLÉ DE L'ÉTAT PAR RÉGION ---
    st.markdown("#### Synthèse chiffrée par région")
    table_reg = summary[["region", "bon_km", "moyen_km", "mauvais_km", "travaux_km", "total_km"]].rename(
        columns={
            "region": "Région",
            "bon_km": "Bon état (km)",
            "moyen_km": "État moyen (km)",
            "mauvais_km": "Mauvais état (km)",
            "travaux_km": "Travaux (km)",
            "total_km": "Total évalué (km)",
        }
    )
    st.dataframe(table_reg.round(1), use_container_width=True, hide_index=True)

    # --- TABLEAU DÉTAILLÉ PAR TRONÇON ---
    with st.expander("🔎 Consulter le détail tronçon par tronçon et méthode d'attribution", expanded=False):
        detail_cols = [
            "troncon", "type_reseau", "region", "source_region",
            "bon_km", "moyen_km", "mauvais_km", "travaux_km", "total_km",
        ]
        table_troncons = routes[detail_cols].rename(
            columns={
                "troncon": "Tronçon routier",
                "type_reseau": "Catégorie",
                "region": "Région",
                "source_region": "Méthode d'attribution",
                "bon_km": "Bon (km)",
                "moyen_km": "Moyen (km)",
                "mauvais_km": "Mauvais (km)",
                "travaux_km": "Travaux (km)",
                "total_km": "Total (km)",
            }
        ).sort_values("Mauvais (km)", ascending=False)
        st.dataframe(table_troncons, use_container_width=True, hide_index=True)

    # --- RAPPEL DES LIMITES STATISTIQUES ---
    routes_classees_all = etat_routes[etat_routes["type_reseau"].str.startswith("Routes")]
    km_non_attrib = routes_classees_all.loc[routes_classees_all["region"] == "Non attribué", "total_km"].sum()
    km_manuel = routes_classees_all.loc[routes_classees_all["source_region"].str.startswith("manuel"), "total_km"].sum()

    data_limitation_box(
        f"1. Millésime unique (2020) : Ces données décrivent l'état du réseau en 2020 et ne permettent pas de mesurer une évolution pluriannuelle.\n"
        f"2. Déduction régionale : Les données brutes ne comportaient pas de colonne région. 99,6% du linéaire a été rattaché via le code de tronçon (TGRK, TGRP, etc.) ou recoupement de nom ; {km_manuel:.1f} km ont été attribués manuellement et {km_non_attrib:.1f} km restent non attribués (exclus des pourcentages régionaux).\n"
        "3. Priorisation des investissements : Le volume de mauvais état ne tient pas compte du niveau de trafic quotidien, du coût au kilomètre ni de la gravité des accidents sur chaque section.",
        title="Limites méthodologiques et attribution géographique"
    )

