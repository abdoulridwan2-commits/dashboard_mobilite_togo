import plotly.express as px
import streamlit as st

from config import COLORS
from utils.components import data_limitation_box, metric_card, render_header, section_title
from utils.data import get_data


def show_accidents():
    data = get_data()
    accidents = data["accidents"]

    render_header()
    section_title("Sécurité routière : Accidents, blessés et décès", "Comptes nationaux, gravité et indicateurs rapportés à la population")

    # --- PANNEAU DE FILTRES ---
    v = st.session_state.get("filter_version", 0)
    with st.expander("🔍 Filtres d'affichage de la sécurité routière", expanded=False):
        col_f1, col_f2 = st.columns(2)

        min_a = int(accidents["annee"].min())
        max_a = int(accidents["annee"].max())

        with col_f1:
            periode_sel = st.slider(
                "Période d'analyse",
                min_value=min_a,
                max_value=max_a,
                value=(min_a, max_a),
                key=f"acc_periode_{v}",
            )

        with col_f2:
            indics_dispo = ["Accidents", "Blessés", "Morts"]
            indics_sel = st.multiselect(
                "Indicateurs affichés",
                options=indics_dispo,
                default=indics_dispo,
                key=f"acc_indics_{v}",
            )



    # --- DONNÉES FILTRÉES ---
    acc_filtre = accidents[accidents["annee"].between(periode_sel[0], periode_sel[1])].copy()

    # --- INDICATEURS CLÉS 2022 (ANNÉE DE RECENSEMENT) ---
    st.markdown("### 📊 Indicateurs de référence (Recensement 2022 : 8 095 498 habitants)")
    acc_2022 = accidents.loc[accidents["annee"] == 2022].iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card(
            label="Accidents (2022)",
            value=f"{int(acc_2022['accidents']):,}".replace(",", " "),
            delta=f"92,8 accidents / 100 000 hab",
            icon="🚨",
            help_text="Tous accidents corporels enregistrés",
        )
    with k2:
        metric_card(
            label="Personnes blessées (2022)",
            value=f"{int(acc_2022['blesses']):,}".replace(",", " "),
            delta=f"{acc_2022['blesses_pour_100k_hab']:.1f} blessés / 100 000 hab",
            icon="🩹",
            help_text="Blessures corporelles documentées",
        )
    with k3:
        metric_card(
            label="Décès enregistrés (2022)",
            value=f"{int(acc_2022['morts']):,}".replace(",", " "),
            delta=f"{acc_2022['morts_pour_100k_hab']:.2f} morts / 100 000 hab",
            icon="⚰️",
            help_text="Tués sur les routes nationales",
        )
    with k4:
        metric_card(
            label="Indice de létalité brute",
            value=f"{acc_2022['deces_pour_100_accidents']:.1f}%",
            delta=f"9,1 décès pour 100 accidents",
            icon="⚠️",
            help_text="Quotient brut morts ÷ accidents",
        )

    # --- GRAPHIQUES D'ÉVOLUTION TEMPORELLE ---
    st.markdown("### 📈 Trajectoire chronologique de l'insécurité routière (2010 – 2022)")

    if not acc_filtre.empty and indics_sel:
        mapping_cols = {"Accidents": "accidents", "Blessés": "blesses", "Morts": "morts"}
        cols_a_garder = [mapping_cols[i] for i in indics_sel]

        acc_long = acc_filtre.melt(
            id_vars=["annee"],
            value_vars=cols_a_garder,
            var_name="indicateur_brut",
            value_name="nombre",
        )
        inv_map = {v: k for k, v in mapping_cols.items()}
        acc_long["Indicateur"] = acc_long["indicateur_brut"].map(inv_map)

        color_map = {
            "Accidents": COLORS["blue"],
            "Blessés": COLORS["accent_dark"],
            "Morts": COLORS["danger"],
        }

        col_g, col_d = st.columns([3, 2])

        with col_g:
            fig_l = px.line(
                acc_long,
                x="annee",
                y="nombre",
                color="Indicateur",
                markers=True,
                title="Évolution annuelle des effectifs enregistrés",
                labels={"annee": "Année", "nombre": "Nombre de personnes / cas", "Indicateur": "Indicateur"},
                color_discrete_map=color_map,
            )
            fig_l.update_layout(
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_l, use_container_width=True)

        with col_d:
            # Graphique de la gravité : létalité brute (morts pour 100 accidents)
            fig_grav = px.bar(
                acc_filtre,
                x="annee",
                y="deces_pour_100_accidents",
                title="Létalité relative (Morts pour 100 accidents)",
                labels={"annee": "Année", "deces_pour_100_accidents": "Morts / 100 accidents (%)"},
                color_discrete_sequence=[COLORS["purple"]],
            )
            fig_grav.update_layout(
                template="plotly_white",
                height=380,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_grav, use_container_width=True)
    else:
        st.info("Veuillez sélectionner au moins un indicateur à afficher.")

    # --- ANALYSE DES RUPTURES ET DES PIÈGES STATISTIQUES ---
    st.markdown("### 🔎 Détection des ruptures de séries et pièges statistiques résolus")

    a_col1, a_col2 = st.columns(2)

    with a_col1:
        st.markdown(
            """
            <div class="panel">
                <h4 style="color: #0a614e; margin-top: 0;">Ruptures notables de la série (2011 & 2016)</h4>
                <p style="font-size: 0.86rem; line-height: 1.5; color: #2c3e40;">
                    La série des accidents enregistre deux variations annuelles supérieures à 50% :
                </p>
                <ul style="font-size: 0.84rem; color: #3d5254; padding-left: 1.2rem;">
                    <li><strong>Année 2011 (+154%) :</strong> Les accidents enregistrés bondissent de 2 153 à 5 464 cas.</li>
                    <li><strong>Année 2016 (+89%) :</strong> Les accidents passent de 4 821 à 9 104 cas.</li>
                </ul>
                <p style="font-size: 0.8rem; color: #5f6f73; margin-top: 0.5rem;">
                    Ces variations brutales s'expliquent généralement par une extension du périmètre de collecte 
                    (intégration de nouveaux commissariats et brigades de gendarmerie) plutôt que par une hausse 
                    purement comportementale.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a_col2:
        st.markdown(
            """
            <div class="panel">
                <h4 style="color: #0a614e; margin-top: 0;">Piège du libellé source résolu</h4>
                <p style="font-size: 0.86rem; line-height: 1.5; color: #2c3e40;">
                    Dans le fichier brut <code>accidents_trafic.csv</code>, une colonne est libellée 
                    <em>« Accidents mortels /100.000 hab »</em> affichant <strong>92,73</strong> en 2022.
                </p>
                <div style="background: #fff8e6; border-left: 3px solid #e8ab39; padding: 0.6rem; border-radius: 4px; font-size: 0.82rem; color: #6b4d00;">
                    <strong>Vérification arithmétique :</strong><br>
                    7 518 accidents ÷ 8 095 498 hab × 100 000 = <strong>92,86</strong>.<br>
                    Le libellé source désigne donc <strong>l'ensemble des accidents</strong> pour 100 000 habitants, 
                    et non les seuls accidents mortels (qui ne font que 8,44 décès / 100k hab).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- LIMITES MÉTHODOLOGIQUES STRICTES ---
    data_limitation_box(
        "1. Aucune donnée géographique : Le fichier source des accidents ne contient aucune information sur les régions, préfectures ou communes. Aucune carte régionale d'accidents ne peut donc être construite sans inventer de données.\n"
        "2. Absence de ventilation par catégorie d'usager : Les données ne précisent pas la part des motos, voitures ou piétons parmi les victimes.\n"
        "3. Taux par habitant limités à 2022 : La population par recensement n'étant disponible que pour 2022, les taux par habitant antérieurs ne sont pas extrapolés arbitrairement.\n"
        "4. Taux par véhicule non calculable : Les immatriculations étant un flux annuel de nouvelles immatriculations et non un stock de véhicules en circulation, aucun ratio d'accidents par véhicule ne peut être calculé de façon rigoureuse.",
        title="Limites méthodologiques indispensables"
    )

