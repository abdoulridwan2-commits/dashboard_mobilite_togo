import plotly.express as px
import streamlit as st

from config import COLORS, PLOTLY_COLOR_DISCRETE
from utils.components import data_limitation_box, metric_card, render_header, section_title
from utils.data import get_data


def show_overview():
    data = get_data()
    vehicules = data["vehicules"]
    accidents = data["accidents"]
    regions = data["regions"]
    auto_ecoles = data["auto_ecoles"]

    render_header()

    # --- CALCULS POUR LES 4 CARTES KPI CLÉS ---
    # 1. Véhicules / Immatriculations
    latest_veh_year = int(vehicules["annee"].max())
    veh_latest = vehicules[vehicules["annee"] == latest_veh_year]
    total_immats_latest = veh_latest["valeur"].sum()
    motos_latest = veh_latest[veh_latest["groupe"] == "Deux-roues"]["valeur"].sum()
    part_motos_latest = (motos_latest / total_immats_latest * 100) if total_immats_latest > 0 else 0

    # 2. Accidents
    latest_acc_year = int(accidents["annee"].max())
    acc_latest = accidents[accidents["annee"] == latest_acc_year].iloc[0]
    total_accidents = int(acc_latest["accidents"])
    total_morts = int(acc_latest["morts"])
    total_blesses = int(acc_latest["blesses"])

    # 3. État du réseau routier
    total_km_reseau = regions["etat_total_km"].sum()
    total_mauvais_km = regions["etat_mauvais_km"].sum()
    part_mauvais_globale = (total_mauvais_km / total_km_reseau * 100) if total_km_reseau > 0 else 0

    # 4. Auto-écoles
    total_auto_ecoles = len(auto_ecoles)
    nb_agreees = int(auto_ecoles["agreee"].sum())
    part_agreees = (nb_agreees / total_auto_ecoles * 100) if total_auto_ecoles > 0 else 0

    # --- AFFICHAGE DES 4 CARTES D'INDICATEURS EN HAUT ---
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        metric_card(
            label="Immatriculations",
            value=f"{int(total_immats_latest):,}".replace(",", " "),
            delta=f"🛵 {part_motos_latest:.1f}% de deux-roues en {latest_veh_year}",
            icon="📋",
            help_text=f"Flux annuel national enregistré en {latest_veh_year}",
        )

    with kpi_col2:
        metric_card(
            label="Accidents de la route",
            value=f"{total_accidents:,}".replace(",", " "),
            delta=f"⚠️ {total_morts:,} morts · {total_blesses:,} blessés ({latest_acc_year})".replace(",", " "),
            icon="🚨",
            help_text="Données nationales officielles de la sécurité routière",
        )

    with kpi_col3:
        metric_card(
            label="État du réseau routier",
            value=f"{part_mauvais_globale:.1f}% dégradé",
            delta=f"🛣️ {total_mauvais_km:,.1f} km en mauvais état (sur {total_km_reseau:,.0f} km)".replace(",", " "),
            icon="🚧",
            help_text="Évaluation 2020 (routes revêtues et en terre)",
        )

    with kpi_col4:
        metric_card(
            label="Auto-écoles recensées",
            value=f"{total_auto_ecoles}",
            delta=f"🎓 {nb_agreees} agréées ({part_agreees:.1f}% du registre)",
            icon="🏫",
            help_text="Points géolocalisés dans le registre national",
        )

    # --- PANNEAU DE FILTRES POUR CETTE PAGE ---
    v = st.session_state.get("filter_version", 0)
    with st.expander("🔍 Filtres d'affichage de la Vue d'ensemble", expanded=False):
        fcol1, fcol2 = st.columns(2)
        min_annee = int(vehicules["annee"].min())
        max_annee = int(vehicules["annee"].max())

        with fcol1:
            annee_range = st.slider(
                "Période d'immatriculation",
                min_value=min_annee,
                max_value=max_annee,
                value=(2000, max_annee),
                key=f"ov_annee_range_{v}",
            )

        with fcol2:
            groupes_dispo = sorted(vehicules["groupe"].dropna().unique().tolist())
            groupes_sel = st.multiselect(
                "Catégories de véhicules",
                options=groupes_dispo,
                default=groupes_dispo,
                key=f"ov_groupes_sel_{v}",
            )



    # --- GRAPHIQUES D'ENSEMBLE ---
    section_title("Dynamiques clés de la mobilité et de la sécurité", "Tendances nationales et disparités territoriales")

    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        st.markdown("#### Évolution du flux d'immatriculations annuelles")
        veh_filtre = vehicules[
            vehicules["annee"].between(annee_range[0], annee_range[1])
            & vehicules["groupe"].isin(groupes_sel)
        ]
        if not veh_filtre.empty:
            agg_veh = veh_filtre.groupby(["annee", "groupe"])["valeur"].sum().reset_index()
            fig_imm = px.line(
                agg_veh,
                x="annee",
                y="valeur",
                color="groupe",
                markers=True,
                labels={"annee": "Année", "valeur": "Immatriculations", "groupe": "Groupe"},
                color_discrete_sequence=PLOTLY_COLOR_DISCRETE,
            )
            fig_imm.update_layout(
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=360,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_imm, use_container_width=True)
        else:
            st.info("Sélectionnez au moins une catégorie de véhicule.")

    with col_droite:
        st.markdown("#### Sécurité routière : Accidents, blessés et morts (2010-2022)")
        acc_long = accidents.melt(
            id_vars=["annee"],
            value_vars=["accidents", "blesses", "morts"],
            var_name="indicateur",
            value_name="nombre",
        )
        dict_labels = {"accidents": "Accidents", "blesses": "Blessés", "morts": "Morts"}
        acc_long["indicateur_label"] = acc_long["indicateur"].map(dict_labels)

        color_acc = {
            "Accidents": COLORS["blue"],
            "Blessés": COLORS["accent_dark"],
            "Morts": COLORS["danger"],
        }
        fig_acc = px.line(
            acc_long,
            x="annee",
            y="nombre",
            color="indicateur_label",
            markers=True,
            labels={"annee": "Année", "nombre": "Nombre de personnes / cas", "indicateur_label": "Indicateur"},
            color_discrete_map=color_acc,
        )
        fig_acc.update_layout(
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_acc, use_container_width=True)

    # --- PANORAMA DU RÉSEAU ET DES AUTO-ÉCOLES PAR RÉGION ---
    col_reg1, col_reg2 = st.columns(2)

    with col_reg1:
        st.markdown("#### État du réseau routier par région (2020)")
        reg_etat = regions[["region", "etat_bon_km", "etat_moyen_km", "etat_mauvais_km", "etat_travaux_km"]].copy()
        reg_etat_long = reg_etat.melt(
            id_vars=["region"],
            var_name="etat",
            value_name="km",
        )
        etat_map = {
            "etat_bon_km": "Bon état",
            "etat_moyen_km": "État moyen",
            "etat_mauvais_km": "Mauvais état",
            "etat_travaux_km": "Travaux en cours",
        }
        reg_etat_long["etat_label"] = reg_etat_long["etat"].map(etat_map)
        color_etat = {
            "Bon état": COLORS["success"],
            "État moyen": COLORS["warning"],
            "Mauvais état": COLORS["danger"],
            "Travaux en cours": COLORS["purple"],
        }
        fig_etat = px.bar(
            reg_etat_long,
            x="region",
            y="km",
            color="etat_label",
            barmode="stack",
            labels={"region": "Région", "km": "Longueur (km)", "etat_label": "État"},
            color_discrete_map=color_etat,
        )
        fig_etat.update_layout(
            template="plotly_white",
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_etat, use_container_width=True)

    with col_reg2:
        st.markdown("#### Répartition territoriale des auto-écoles recensées")
        auto_par_reg = auto_ecoles.groupby(["region", "statut"]).size().reset_index(name="nb")
        fig_ae = px.bar(
            auto_par_reg,
            x="region",
            y="nb",
            color="statut",
            barmode="stack",
            labels={"region": "Région", "nb": "Nombre d'auto-écoles", "statut": "Statut d'agrément"},
            color_discrete_sequence=[COLORS["primary"], COLORS["accent"], COLORS["purple"], COLORS["muted"]],
        )
        fig_ae.update_layout(
            template="plotly_white",
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_ae, use_container_width=True)

    # --- CONSTATS MESURÉS ET LIMITES ---
    st.markdown("### 📊 Constats mesurés majeurs")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f"""
            - **Quadruplement des immatriculations :** Le flux annuel est passé d'environ 15 000 au début des années 2000 à plus de **{int(total_immats_latest):,}** en {latest_veh_year}, porté à plus de **{part_motos_latest:.1f}%** par les deux-roues.
            - **Bilan d'insécurité routière élevé :** En {latest_acc_year}, le Togo enregistre **{total_accidents:,} accidents**, **{total_blesses:,} blessés** et **{total_morts:,} décès**, soit une létalité brute de **{(total_morts / total_accidents * 100):.1f} morts pour 100 accidents**.
            """.replace(",", " ")
        )

    with c2:
        pire_part_reg = regions.sort_values("part_mauvais_pct", ascending=False).iloc[0]
        pire_km_reg = regions.sort_values("etat_mauvais_km", ascending=False).iloc[0]
        st.markdown(
            f"""
            - **Fragilité du réseau routier (2020) :** La région **{pire_part_reg['region']}** présente la plus forte proportion de routes dégradées (**{pire_part_reg['part_mauvais_pct']:.1f}%**), tandis que la région **{pire_km_reg['region']}** concentre le plus grand volume kilométrique dégradé (**{pire_km_reg['etat_mauvais_km']:.1f} km**).
            - **Hyper-concentration des auto-écoles :** La région Maritime concentre la grande majorité des établissements recensés, tandis que plusieurs préfectures de l'intérieur n'ont aucune structure enregistrée.
            """
        )

    data_limitation_box(
        "1. Les données d'accidents sont disponibles uniquement à l'échelle nationale : aucune ventilation géographique par région ou préfecture n'est fournie.\n"
        "2. Les données de parc représentent des immatriculations annuelles (flux de nouvelles cartes grises) et non le parc cumulé en circulation active.\n"
        "3. L'état du réseau routier correspond à un millésime unique (2020), ne permettant pas de mesurer une évolution temporelle.\n"
        "4. Le fichier des auto-écoles est un inventaire sans date d'observation ni garantie d'exhaustivité.",
        title="Rappel strict des limites méthodologiques des données"
    )
