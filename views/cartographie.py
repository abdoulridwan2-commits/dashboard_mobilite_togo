from html import escape

import folium
import pandas as pd
import streamlit as st
from shapely.errors import ShapelyError
from shapely import wkt
from shapely.geometry import mapping
from streamlit_folium import st_folium

from utils.components import render_header, section_title
from utils.data import get_data


def show_cartographie():
    data = get_data()
    routes = data["routes"]
    auto_ecoles = data["auto_ecoles"]
    prefectures_data = data["prefectures"]

    render_header()
    section_title("Routes classées et auto-écoles")
    st.caption(
        "Les lignes représentent les géométries des routes classées; les points représentent les entrées "
        "de l’inventaire d’auto-écoles. Une absence de point ou de tronçon dans les fichiers ne prouve pas "
        "l’absence réelle de service ou de route."
    )

    regions = sorted(prefectures_data["region"].dropna().unique().tolist())
    region_options = ["Toutes"] + regions
    region = st.selectbox("Région", region_options, key="map_region")
    routes_in_region = routes if region == "Toutes" else routes[routes["region"] == region]
    schools_in_region = auto_ecoles if region == "Toutes" else auto_ecoles[auto_ecoles["region"] == region]
    prefecture_rows = prefectures_data
    if region != "Toutes":
        prefecture_rows = prefecture_rows[prefecture_rows["region"] == region]
    prefectures = sorted(prefecture_rows["prefecture"].dropna().unique().tolist())
    prefecture = st.selectbox(
        "Préfecture",
        ["Toutes"] + prefectures,
        key="map_prefecture",
    )
    if prefecture != "Toutes":
        routes_in_region = routes_in_region[routes_in_region["prefecture"] == prefecture]
        schools_in_region = schools_in_region[schools_in_region["prefecture"] == prefecture]

    route_count, school_count = st.columns(2)
    route_count.metric("Tracés de routes classées", f"{len(routes_in_region):,}")
    school_count.metric("Auto-écoles listées", f"{len(schools_in_region):,}")
    if prefecture != "Toutes" and routes_in_region.empty and schools_in_region.empty:
        st.warning(
            "Aucune ligne de route classée ni d’auto-école n’est présente pour cette préfecture dans les fichiers. "
            "Cela ne permet pas de conclure à l’absence de routes ou de services sur le terrain."
        )

    map_view = folium.Map(
        location=[8.6, 0.8],
        zoom_start=6 if region == "Toutes" else 8,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    route_colors = {
        "Route nationale revêtue": "#178755",
        "Route nationale non revêtue": "#c77b10",
        "Voirie urbaine": "#2776b7",
        "Piste rurale": "#a34040",
    }

    features = []
    invalid_geometry = 0
    for row in routes_in_region.itertuples(index=False):
        try:
            geometry = mapping(wkt.loads(row.geometry_wkt))
        except (ShapelyError, TypeError, ValueError):
            invalid_geometry += 1
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "route_nom": row.route_nom or "Non renseigné",
                    "type_route": row.type_route,
                    "revetement": row.revetement or "Non renseigné",
                    "longueur_km": float(row.longueur_km),
                    "region": row.region,
                    "prefecture": row.prefecture,
                },
            }
        )

    if features:
        folium.GeoJson(
            {"type": "FeatureCollection", "features": features},
            name="Routes classées",
            style_function=lambda feature: {
                "color": route_colors.get(feature["properties"]["type_route"], "#526d78"),
                "weight": 3 if "nationale" in feature["properties"]["type_route"].lower() else 2,
                "opacity": 0.8,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["route_nom", "type_route", "revetement", "longueur_km", "region", "prefecture"],
                aliases=["Route", "Classification", "Revêtement", "Longueur (km)", "Région", "Préfecture"],
                sticky=False,
            ),
        ).add_to(map_view)

    school_layer = folium.FeatureGroup(name="Auto-écoles listées", show=True)
    for row in schools_in_region.itertuples(index=False):
        if pd.isna(row.latitude) or pd.isna(row.longitude):
            continue
        color = "#178755" if row.agreee else "#c77b10"
        if row.statut == "Non renseigné":
            color = "#687a80"
        popup = (
            f"<b>{escape(str(row.nom))}</b><br>"
            f"{escape(str(row.statut))}<br>"
            f"{escape(str(row.region))} · {escape(str(row.prefecture))}"
        )
        folium.CircleMarker(
            location=[row.latitude, row.longitude],
            radius=5,
            color="white",
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=folium.Popup(popup, max_width=280),
        ).add_to(school_layer)
    school_layer.add_to(map_view)
    folium.LayerControl(collapsed=False).add_to(map_view)

    st_folium(map_view, height=600, use_container_width=True, returned_objects=[], key="territorial_map")
    if invalid_geometry:
        st.warning(f"{invalid_geometry} géométrie(s) de route n’ont pas pu être interprétées et ne sont pas affichées.")
    st.caption(
        "Classification des routes par type; la couche d’état est distincte et datée de 2020. "
        "Les routes et l’état ne doivent pas être confondus."
    )
