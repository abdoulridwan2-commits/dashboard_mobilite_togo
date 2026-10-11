from html import escape

import folium
import pandas as pd
import streamlit as st
from shapely import wkt
from shapely.errors import ShapelyError
from shapely.geometry import mapping
from streamlit_folium import st_folium

from config import COLORS
from utils.components import data_limitation_box, metric_card, render_header, section_title
from utils.data import get_data


def show_cartographie():
    data = get_data()
    routes = data["routes"]
    auto_ecoles = data["auto_ecoles"]
    prefectures_data = data["prefectures"]

    render_header()
    section_title("Cartographie interactive du réseau classé et des auto-écoles", "Visualisation spatiale des infrastructures et des équipements de formation")

    # --- PANNEAU DE FILTRES ---
    v = st.session_state.get("filter_version", 0)
    with st.expander("🔍 Filtres géographiques et thématiques", expanded=False):
        col_f1, col_f2, col_f3 = st.columns(3)

        regions_dispo = sorted(prefectures_data["region"].dropna().unique().tolist())
        with col_f1:
            reg_sel = st.selectbox("Région", ["Toutes les régions"] + regions_dispo, key=f"map_reg_sel_{v}")

        # Préfecture conditionnelle
        pref_subset = prefectures_data
        if reg_sel != "Toutes les régions":
            pref_subset = pref_subset[pref_subset["region"] == reg_sel]
        pref_dispo = sorted(pref_subset["prefecture"].dropna().unique().tolist())
        pref_options = ["Toutes les préfectures"] + pref_dispo

        with col_f2:
            pref_sel = st.selectbox("Préfecture", pref_options, key=f"map_pref_sel_{v}")

        # Type de route
        type_routes_dispo = sorted(routes["type_route"].dropna().unique().tolist())
        with col_f3:
            type_sel = st.selectbox("Type de route", ["Tous les types"] + type_routes_dispo, key=f"map_type_sel_{v}")



    # --- APPLICATION DES FILTRES ---
    routes_f = routes.copy()
    ae_f = auto_ecoles.copy()
    pref_f = prefectures_data.copy()

    if reg_sel != "Toutes les régions":
        routes_f = routes_f[routes_f["region"] == reg_sel]
        ae_f = ae_f[ae_f["region"] == reg_sel]
        pref_f = pref_f[pref_f["region"] == reg_sel]

    if pref_sel != "Toutes les préfectures":
        routes_f = routes_f[routes_f["prefecture"] == pref_sel]
        ae_f = ae_f[ae_f["prefecture"] == pref_sel]
        pref_f = pref_f[pref_f["prefecture"] == pref_sel]

    if type_sel != "Tous les types":
        routes_f = routes_f[routes_f["type_route"] == type_sel]

    # --- CARTES KPI CONTEXTUELLES ---
    k1, k2, k3, k4 = st.columns(4)
    total_km_carte = routes_f["longueur_km"].sum()
    nb_ae_carte = len(ae_f)
    nb_ae_agreees_carte = int(ae_f["agreee"].sum())
    pop_territoire = pref_f["population_2022"].sum()

    with k1:
        metric_card(
            label="Tracés de routes",
            value=f"{len(routes_f):,}".replace(",", " "),
            delta=f"{total_km_carte:,.1f} km au total".replace(",", " "),
            icon="🛣️",
        )
    with k2:
        ratio_routes_pop = (total_km_carte / pop_territoire * 1000) if pop_territoire > 0 else 0
        metric_card(
            label="Desserte routière",
            value=f"{ratio_routes_pop:.2f} km",
            delta="pour 1 000 habitants",
            icon="👥",
            help_text=f"Pop. réf : {pop_territoire:,} hab".replace(",", " "),
        )
    with k3:
        metric_card(
            label="Auto-écoles affichées",
            value=f"{nb_ae_carte}",
            delta=f"🎓 {nb_ae_agreees_carte} agréées",
            icon="🏫",
        )
    with k4:
        ratio_ae_pop = (nb_ae_carte / pop_territoire * 100000) if pop_territoire > 0 else 0
        metric_card(
            label="Densité de formation",
            value=f"{ratio_ae_pop:.2f}",
            delta="auto-écoles / 100 000 hab",
            icon="📍",
            help_text="Ratio descriptif recensement 2022",
        )

    # Alerte spécifique si préfecture sans données géographiques (ex: Mô)
    if pref_sel != "Toutes les préfectures" and routes_f.empty and ae_f.empty:
        st.warning(
            f"ℹ️ **Préfecture de {pref_sel} :** Aucun segment de route classée ni auto-école n'est recensé dans les fichiers géographiques fournis. "
            "Conformément à la rigueur méthodologique, cela reflète une absence d'entrée dans le jeu de données et non l'absence réelle d'infrastructures ou de services sur le terrain."
        )

    # --- CONSTRUCTION DE LA CARTE FOLIUM ---
    centre_map = [8.6, 1.1]
    zoom_map = 7
    if reg_sel != "Toutes les régions":
        zoom_map = 8
    if pref_sel != "Toutes les préfectures":
        zoom_map = 9

    # Si auto-écoles avec coordonnées, centrer sur leur moyenne
    if not ae_f.empty and ae_f["latitude"].notna().any():
        centre_map = [float(ae_f["latitude"].mean()), float(ae_f["longitude"].mean())]

    carte = folium.Map(
        location=centre_map,
        zoom_start=zoom_map,
        tiles="CartoDB positron",
        control_scale=True,
    )

    # Styles et couleurs des routes
    route_colors = {
        "Route nationale revêtue": COLORS["primary"],
        "Route nationale non revêtue": COLORS["accent_dark"],
        "Voirie urbaine": COLORS["blue"],
        "Piste rurale": "#d05454",
    }

    # Couche des routes
    features = []
    geom_invalides = 0
    # Limiter les features à 500 max pour la réactivité si pas filtré
    routes_a_afficher = routes_f.head(600)
    for row in routes_a_afficher.itertuples(index=False):
        try:
            geom = mapping(wkt.loads(row.geometry_wkt))
        except (ShapelyError, TypeError, ValueError):
            geom_invalides += 1
            continue

        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "route_nom": row.route_nom or "Non renseigné",
                "type_route": row.type_route,
                "revetement": row.revetement or "Non renseigné",
                "longueur_km": float(row.longueur_km),
                "region": row.region,
                "prefecture": row.prefecture,
            },
        })

    if features:
        folium.GeoJson(
            {"type": "FeatureCollection", "features": features},
            name="🛣️ Tracés des routes classées",
            style_function=lambda feature: {
                "color": route_colors.get(feature["properties"]["type_route"], "#4a5568"),
                "weight": 3.5 if "nationale" in str(feature["properties"]["type_route"]).lower() else 2,
                "opacity": 0.85,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["route_nom", "type_route", "revetement", "longueur_km", "region", "prefecture"],
                aliases=["Route", "Type", "Revêtement", "Longueur (km)", "Région", "Préfecture"],
                sticky=False,
            ),
        ).add_to(carte)

    # Couche des auto-écoles
    layer_ae = folium.FeatureGroup(name="🏫 Auto-écoles recensées", show=True)
    for row in ae_f.itertuples(index=False):
        if pd.isna(row.latitude) or pd.isna(row.longitude):
            continue

        # Vert pour agréée, jaune/orange pour non agréée, violet pour antenne, gris sinon
        if row.statut == "Agréée":
            color_point = COLORS["primary"]
        elif row.statut == "Antenne agréée":
            color_point = COLORS["purple"]
        elif row.statut == "Non agréée":
            color_point = COLORS["accent_dark"]
        else:
            color_point = "#718096"

        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px; min-width: 180px;">
            <b style="color: #0a614e; font-size: 13px;">{escape(str(row.nom))}</b><br>
            <span style="display:inline-block; padding: 2px 6px; border-radius: 4px; font-weight: bold; background: #eef7f4; color: #0a614e; margin: 4px 0;">{escape(str(row.statut))}</span><br>
            <b>Territoire :</b> {escape(str(row.region))} · {escape(str(row.prefecture))}<br>
            <b>Localité :</b> {escape(str(row.localite)) if pd.notna(row.localite) else 'N/A'}<br>
            <b>Jours :</b> {escape(str(row.jours_ouverture)) if pd.notna(row.jours_ouverture) else 'Non renseigné'}
        </div>
        """

        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=6,
            color="#ffffff",
            weight=1.5,
            fill=True,
            fill_color=color_point,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{escape(str(row.nom))} ({row.statut})",
        ).add_to(layer_ae)

    layer_ae.add_to(carte)
    folium.LayerControl(collapsed=False).add_to(carte)

    # Légende visuelle en bandeau
    st.markdown(
        """
        <div style="display: flex; gap: 15px; flex-wrap: wrap; background: #ffffff; border: 1px solid #e2ece7; border-radius: 8px; padding: 8px 14px; margin-bottom: 10px; font-size: 0.8rem;">
            <span><strong>Routes :</strong></span>
            <span><span style="color:#0f8f73;">■</span> Route nationale revêtue</span>
            <span><span style="color:#d4a409;">■</span> Route nationale non revêtue</span>
            <span><span style="color:#2b6cb0;">■</span> Voirie urbaine</span>
            <span><span style="color:#d05454;">■</span> Piste rurale</span>
            <span style="margin-left: 15px;"><strong>Auto-écoles :</strong></span>
            <span><span style="color:#0f8f73;">●</span> Agréée</span>
            <span><span style="color:#7b2cbf;">●</span> Antenne agréée</span>
            <span><span style="color:#d4a409;">●</span> Non agréée</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st_folium(carte, height=580, use_container_width=True, returned_objects=[], key="carto_togo_map")

    data_limitation_box(
        "1. Tracés des routes classées : Les géométries représentent l'inventaire des routes classées togolaises et ne doivent pas être confondues avec la couche d'état d'entretien (qui est une table distincte datée de 2020).\n"
        "2. Inventaire des auto-écoles : Les points proviennent du registre sans mention de millésime ni d'exhaustivité. Une préfecture sans point indique une absence d'enregistrement dans le fichier, et non la preuve sur le terrain d'une absence de service.\n"
        "3. Ratios calculés : Les ratios de km routiers et d'auto-écoles sont rapportés à la population du recensement 2022.",
        title="Précisions sur les données cartographiques"
    )

