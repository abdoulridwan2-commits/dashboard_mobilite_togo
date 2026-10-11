import plotly.express as px
import streamlit as st

from config import COLORS
from utils.components import data_limitation_box, metric_card, render_header, section_title
from utils.data import get_data


def show_auto_ecoles():
    data = get_data()
    auto_ecoles = data["auto_ecoles"]
    pref = data["prefectures"]

    render_header()
    section_title("Maillage territorial des auto-écoles et accès à la formation", "Répartition géographique, statuts d'agrément et ratios par habitant")

    # --- PANNEAU DE FILTRES ---
    v = st.session_state.get("filter_version", 0)
    with st.expander("🔍 Filtres d'affichage des auto-écoles", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)

        regions_dispo = sorted(pref["region"].dropna().unique().tolist())
        with col_f1:
            reg_sel = st.selectbox("Région", ["Toutes les régions"] + regions_dispo, key=f"ae_reg_sel_{v}")

        pref_subset = pref
        if reg_sel != "Toutes les régions":
            pref_subset = pref_subset[pref_subset["region"] == reg_sel]
        pref_dispo = sorted(pref_subset["prefecture"].dropna().unique().tolist())
        pref_options = ["Toutes les préfectures"] + pref_dispo

        with col_f2:
            pref_sel = st.selectbox("Préfecture", pref_options, key=f"ae_pref_sel_{v}")

        statuts_dispo = sorted(auto_ecoles["statut"].dropna().unique().tolist())
        with col_f3:
            statut_sel = st.selectbox("Statut d'agrément", ["Tous les statuts"] + statuts_dispo, key=f"ae_statut_sel_{v}")



    # --- FILTRAGE DES DONNÉES ---
    ae_f = auto_ecoles.copy()
    pref_f = pref.copy()

    if reg_sel != "Toutes les régions":
        ae_f = ae_f[ae_f["region"] == reg_sel]
        pref_f = pref_f[pref_f["region"] == reg_sel]

    if pref_sel != "Toutes les préfectures":
        ae_f = ae_f[ae_f["prefecture"] == pref_sel]
        pref_f = pref_f[pref_f["prefecture"] == pref_sel]

    if statut_sel != "Tous les statuts":
        ae_f = ae_f[ae_f["statut"] == statut_sel]

    # --- CARTES KPI ---
    k1, k2, k3, k4 = st.columns(4)
    total_ae = len(ae_f)
    nb_agreees = int(ae_f["agreee"].sum())
    pop_tot = pref_f["population_2022"].sum()
    pref_sans_ae = pref_f[~pref_f["auto_ecoles_entree_presente"]]

    with k1:
        metric_card(
            label="Établissements recensés",
            value=f"{total_ae}",
            delta=f"Sur le territoire sélectionné",
            icon="🏫",
        )
    with k2:
        part_agreees = (nb_agreees / total_ae * 100) if total_ae > 0 else 0
        metric_card(
            label="Taux d'agrément",
            value=f"{part_agreees:.1f}%",
            delta=f"🎓 {nb_agreees} agréées ou antennes",
            icon="📜",
        )
    with k3:
        taux_100k = (total_ae / pop_tot * 100000) if pop_tot > 0 else 0
        metric_card(
            label="Taux pour 100 000 hab",
            value=f"{taux_100k:.2f}",
            delta=f"Pop. réf : {pop_tot:,} hab".replace(",", " "),
            icon="👥",
            help_text="Recensement 2022",
        )
    with k4:
        metric_card(
            label="Préfectures sans entrée",
            value=f"{len(pref_sans_ae)}",
            delta=f"Sur {len(pref_f)} préfectures affichées",
            icon="📍",
            help_text="Non répertoriées dans le registre",
        )

    # --- ANALYSE DE LA CONCENTRATION ET DES STATUTS ---
    st.markdown("### 📊 Répartition géographique et statut d'agrément")

    col_g, col_d = st.columns(2)

    with col_g:
        st.markdown("#### Répartition par statut juridique d'agrément")
        statut_counts = ae_f["statut"].value_counts().reset_index()
        statut_counts.columns = ["Statut", "Nombre"]

        fig_st = px.pie(
            statut_counts,
            names="Statut",
            values="Nombre",
            hole=0.45,
            color="Statut",
            color_discrete_map={
                "Agréée": COLORS["primary"],
                "Antenne agréée": COLORS["purple"],
                "Non agréée": COLORS["accent_dark"],
                "Non renseigné": "#a0aec0",
            },
        )
        fig_st.update_layout(
            template="plotly_white",
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_st, use_container_width=True)

    with col_d:
        st.markdown("#### Nombre d'auto-écoles par région")
        reg_counts = ae_f.groupby(["region", "agreee"]).size().reset_index(name="Nombre")
        reg_counts["Statut_label"] = reg_counts["agreee"].map({True: "Agréée / Antenne", False: "Non agréée / Autre"})

        fig_reg = px.bar(
            reg_counts,
            x="region",
            y="Nombre",
            color="Statut_label",
            barmode="stack",
            labels={"region": "Région", "Nombre": "Auto-écoles", "Statut_label": "Agrément"},
            color_discrete_map={
                "Agréée / Antenne": COLORS["primary"],
                "Non agréée / Autre": COLORS["accent_dark"],
            },
        )
        fig_reg.update_layout(
            template="plotly_white",
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    # --- CLASSEMENT DES PRÉFECTURES ET COUVERTURE PAR HABITANT ---
    st.markdown("### 🏛️ Disparités préfectorales de couverture (Auto-écoles pour 100 000 hab)")

    fig_pref = px.bar(
        pref_f.sort_values("auto_ecoles_pour_100k_hab", ascending=False).head(20),
        x="prefecture",
        y="auto_ecoles_pour_100k_hab",
        color="region",
        labels={"prefecture": "Préfecture", "auto_ecoles_pour_100k_hab": "Auto-écoles / 100k hab", "region": "Région"},
        title="Top 20 des préfectures par taux d'auto-écoles pour 100 000 habitants",
        color_discrete_sequence=[COLORS["primary"], COLORS["accent"], COLORS["blue"], COLORS["purple"], "#d05454"],
    )
    fig_pref.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig_pref, use_container_width=True)

    # --- TABLEAU DÉTAILLÉ PAR PRÉFECTURE ---
    st.markdown("#### Tableau complet des indicateurs préfectoraux")
    table_pref = pref_f[[
        "prefecture", "region", "population_2022", "auto_ecoles",
        "auto_ecoles_agreees", "auto_ecoles_pour_100k_hab", "auto_ecoles_entree_presente"
    ]].rename(
        columns={
            "prefecture": "Préfecture",
            "region": "Région",
            "population_2022": "Population (2022)",
            "auto_ecoles": "Auto-écoles recensées",
            "auto_ecoles_agreees": "Dont agréées",
            "auto_ecoles_pour_100k_hab": "Taux / 100k hab",
            "auto_ecoles_entree_presente": "Entrée présente dans registre",
        }
    ).sort_values("Auto-écoles recensées", ascending=False)

    st.dataframe(table_pref, use_container_width=True, hide_index=True)

    data_limitation_box(
        "1. Date et exhaustivité de l'inventaire : Le fichier ne précise pas l'année d'observation ni s'il s'agit d'un recensement exhaustif ou d'un registre partiel des établissements déclarés.\n"
        "2. Absence d'entrée ≠ absence réelle de service : Si une préfecture affiche 0 entrée, cela signifie qu'aucun établissement n'est consigné dans ce fichier précis ; cela ne prouve pas l'inexistence sur le terrain d'initiatives ou d'antennes non enregistrées.\n"
        "3. Taux descriptif : Le ratio pour 100 000 habitants utilise la population officielle du recensement 2022 à titre comparatif.",
        title="Précautions d'interprétation pour les auto-écoles"
    )

