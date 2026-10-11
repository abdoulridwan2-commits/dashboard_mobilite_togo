import pandas as pd
import plotly.express as px
import streamlit as st

from config import COLORS, PLOTLY_COLOR_DISCRETE
from utils.components import data_limitation_box, metric_card, render_header, section_title
from utils.data import get_data


def show_vehicules_permis():
    data = get_data()
    vehicules = data["vehicules"]
    permis = data["permis"]

    render_header()
    section_title("Évolution des immatriculations et des permis de conduire", "Analyse nationale de la mobilité et de la formation")

    # --- PANNEAU DE FILTRES ---
    v = st.session_state.get("filter_version", 0)
    with st.expander("🔍 Filtres d'affichage (Période & Catégories)", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            periode_sel = st.slider(
                "Période d'observation",
                min_value=2007,
                max_value=2022,
                value=(2007, 2022),
                key=f"vp_periode_{v}",
            )

        with col_f2:
            groupes_dispo = sorted(vehicules["groupe"].dropna().unique().tolist())
            groupes_sel = st.multiselect(
                "Catégories de véhicules",
                options=groupes_dispo,
                default=groupes_dispo,
                key=f"vp_groupes_{v}",
            )

        with col_f3:
            permis_dispo = sorted(permis["libelle"].dropna().unique().tolist())
            permis_sel = st.multiselect(
                "Catégories de permis",
                options=permis_dispo,
                default=permis_dispo,
                key=f"vp_permis_{v}",
            )



    # --- DONNÉES FILTRÉES ---
    veh_f = vehicules[
        vehicules["annee"].between(periode_sel[0], periode_sel[1])
        & vehicules["groupe"].isin(groupes_sel)
    ]
    per_f = permis[
        permis["annee"].between(periode_sel[0], periode_sel[1])
        & permis["libelle"].isin(permis_sel)
    ]

    # --- CARTES MÉTRIQUES SUR LA PÉRIODE SÉLECTIONNÉE ---
    c1, c2, c3, c4 = st.columns(4)
    total_veh_periode = veh_f["valeur"].sum()
    motos_periode = veh_f[veh_f["groupe"] == "Deux-roues"]["valeur"].sum()
    total_permis_periode = per_f["valeur"].sum()
    permis_moto_periode = per_f[per_f["categorie"] == "A"]["valeur"].sum()

    with c1:
        metric_card(
            label="Total immatriculations",
            value=f"{int(total_veh_periode):,}".replace(",", " "),
            delta=f"Période {periode_sel[0]}-{periode_sel[1]}",
            icon="🚗",
        )
    with c2:
        part_motos = (motos_periode / total_veh_periode * 100) if total_veh_periode > 0 else 0
        metric_card(
            label="Deux-roues immatriculés",
            value=f"{int(motos_periode):,}".replace(",", " "),
            delta=f"{part_motos:.1f}% des flux de la sélection",
            icon="🛵",
        )
    with c3:
        metric_card(
            label="Total permis délivrés",
            value=f"{int(total_permis_periode):,}".replace(",", " "),
            delta="Toutes catégories A à F",
            icon="💳",
        )
    with c4:
        ratio_moto = (permis_moto_periode / motos_periode * 100) if motos_periode > 0 else 0
        metric_card(
            label="Permis Moto (A) délivrés",
            value=f"{int(permis_moto_periode):,}".replace(",", " "),
            delta=f"Soit ~{ratio_moto:.1f}% des 2-roues entrés",
            icon="⚠️",
            help_text="Écart structurel d'accès au permis",
        )

    # --- GRAPHIQUES CÔTE À CÔTE ---
    col_g, col_d = st.columns(2)

    with col_g:
        st.markdown("#### 1. Flux annuel d'immatriculations par groupe")
        if not veh_f.empty:
            agg_v = veh_f.groupby(["annee", "groupe"])["valeur"].sum().reset_index()
            fig_v = px.line(
                agg_v,
                x="annee",
                y="valeur",
                color="groupe",
                markers=True,
                labels={"annee": "Année", "valeur": "Immatriculations", "groupe": "Groupe"},
                color_discrete_sequence=PLOTLY_COLOR_DISCRETE,
            )
            fig_v.update_traces(connectgaps=False)
            fig_v.update_layout(
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_v, use_container_width=True)
        else:
            st.info("Aucune donnée d'immatriculation pour cette sélection.")

    with col_d:
        st.markdown("#### 2. Permis de conduire délivrés par catégorie")
        if not per_f.empty:
            fig_p = px.line(
                per_f,
                x="annee",
                y="valeur",
                color="libelle",
                markers=True,
                labels={"annee": "Année", "valeur": "Permis délivrés", "libelle": "Catégorie"},
                color_discrete_sequence=[COLORS["accent"], COLORS["blue"], COLORS["primary"], COLORS["purple"], "#d05454", "#6c757d"],
            )
            fig_p.update_traces(connectgaps=False)
            fig_p.update_layout(
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("Aucune donnée de permis pour cette sélection.")

    # Alerte spécifique pour 2013
    st.warning(
        "⚠️ **Année 2013 (Données de permis manquantes) :** "
        "Dans la source officielle, le total des permis 2013 est à 0 et aucune valeur par catégorie n'est fournie. "
        "Conformément aux règles de qualité, ces données sont laissées vides (`NaN`) et ne sont pas assimilées à zéro."
    )

    # --- FOCUS : LE DÉCROCHAGE MOTOS VS PERMIS A ---
    st.markdown("### 🔍 Analyse de l'écart : Deux-roues vs Permis Moto (Catégorie A)")
    f_col1, f_col2 = st.columns([3, 2])

    with f_col1:
        # Table de comparaison annuelle
        v_moto = vehicules[vehicules["groupe"] == "Deux-roues"].groupby("annee")["valeur"].sum().rename("Immatriculations Deux-roues")
        p_moto = permis[permis["categorie"] == "A"].set_index("annee")["valeur"].rename("Permis A délivrés")
        comp_moto = pd.concat([v_moto, p_moto], axis=1).loc[2007:2022].reset_index()
        comp_moto["Écart annuel"] = comp_moto["Immatriculations Deux-roues"] - comp_moto["Permis A délivrés"]
        comp_moto["Ratio Permis A / Motos (%)"] = (comp_moto["Permis A délivrés"] / comp_moto["Immatriculations Deux-roues"] * 100).round(1)

        fig_gap = px.bar(
            comp_moto,
            x="annee",
            y=["Immatriculations Deux-roues", "Permis A délivrés"],
            barmode="group",
            labels={"annee": "Année", "value": "Volume annuel", "variable": "Indicateur"},
            color_discrete_map={
                "Immatriculations Deux-roues": COLORS["primary"],
                "Permis A délivrés": COLORS["accent_dark"],
            },
        )
        fig_gap.update_layout(
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=320,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_gap, use_container_width=True)

    with f_col2:
        st.markdown(
            """
            <div class="panel">
                <h4 style="color: #0a614e; margin-top: 0;">Le fossé de formalisation des motocyclistes</h4>
                <p style="font-size: 0.88rem; line-height: 1.5; color: #2c3e40;">
                    Alors que les deux-roues représentent la force motrice de la mobilité urbaine togolaise 
                    (plus de 40 000 à 45 000 nouvelles immatriculations par an récemment), 
                    le nombre de permis moto délivrés est resté historiquement sous la barre des 1 000 par an, 
                    avec un rebond récent (4 837 en 2022).
                </p>
                <div style="background: #eef7f4; border-radius: 8px; padding: 0.6rem 0.8rem; margin: 0.6rem 0; font-size: 0.82rem; font-weight: 600; color: #0a614e;">
                    👉 Moins de 10% des conducteurs de deux-roues entrants disposent d'un permis A officiel délivré la même année !
                </div>
                <p style="font-size: 0.8rem; color: #5f6f73; margin: 0;">
                    Ce décalage massif constitue un levier prioritaire de politique publique pour la sécurité routière.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- COMPARAISON EN INDICE BASE 100 ---
    st.markdown("### 📈 Comparaison des dynamiques de croissance (Indice Base 100)")
    st.caption(
        "L'indice base 100 compare les variations relatives et les vitesses d'évolution, pas les volumes absolus. "
        "L'année de référence (100) est la première année commune renseignée de la sélection."
    )

    b1, b2 = st.columns(2)
    with b1:
        sel_g = st.selectbox(
            "Sélectionner un groupe de véhicules",
            groupes_dispo,
            index=groupes_dispo.index("Deux-roues") if "Deux-roues" in groupes_dispo else 0,
            key=f"comparison_vehicle_group_{v}",
        )
    with b2:
        sel_c = st.selectbox(
            "Sélectionner une catégorie de permis",
            permis_dispo,
            index=0,
            key=f"comparison_permit_category_{v}",
        )


    s_veh = vehicules[vehicules["groupe"] == sel_g].groupby("annee")["valeur"].sum().rename(f"Véhicules ({sel_g})")
    s_per = permis[permis["libelle"] == sel_c].set_index("annee")["valeur"].rename(f"Permis ({sel_c})")
    comp_df = pd.concat([s_veh, s_per], axis=1).loc[periode_sel[0]:periode_sel[1]]

    # Calcul de l'indice
    comp_clean = comp_df.dropna()
    if not comp_clean.empty:
        annee_base = int(comp_clean.index.min())
        val_base_v = comp_clean.loc[annee_base, f"Véhicules ({sel_g})"]
        val_base_p = comp_clean.loc[annee_base, f"Permis ({sel_c})"]

        if val_base_v > 0 and val_base_p > 0:
            comp_idx = comp_df.copy()
            comp_idx[f"Véhicules ({sel_g})"] = comp_idx[f"Véhicules ({sel_g})"] / val_base_v * 100
            comp_idx[f"Permis ({sel_c})"] = comp_idx[f"Permis ({sel_c})"] / val_base_p * 100
            comp_idx = comp_idx.reset_index().melt(id_vars=["annee"], var_name="Série", value_name="Indice base 100")

            fig_idx = px.line(
                comp_idx,
                x="annee",
                y="Indice base 100",
                color="Série",
                markers=True,
                title=f"Indice 100 fixé en {annee_base}",
                color_discrete_sequence=[COLORS["primary"], COLORS["purple"]],
            )
            fig_idx.update_traces(connectgaps=False)
            fig_idx.update_layout(template="plotly_white", height=320)
            st.plotly_chart(fig_idx, use_container_width=True)
        else:
            st.info("La valeur de base en année initiale est nulle, calcul d'indice impossible.")
    else:
        st.info("Aucune année commune non-vide pour calculer la base 100.")

    data_limitation_box(
        "Les immatriculations décrivent un flux annuel de nouvelles cartes grises délivrées par la Direction des Transports Routiers et Ferroviaires (DTRF), "
        "et non le nombre total de véhicules roulant effectivement sur les routes togolaises (qui dépend des sorties de parc, pannes, accidents, etc.). "
        "De plus, les permis délivrés correspondent à des nouveaux titres et ne renseignent pas sur le stock historique cumulé de titulaires.",
        title="Distinction fondamentale flux annuel vs parc roulant"
    )
