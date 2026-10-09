import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_recommandations():
    data = get_data()
    vehicules = data["vehicules"]
    accidents = data["accidents"]
    regions = data["regions"]
    auto_ecoles = data["auto_ecoles"]
    prefectures = data["prefectures"]

    render_header()
    section_title("Recommandations fondées sur les données disponibles")
    st.caption(
        "Les priorités ci-dessous sont des pistes d’action, pas des preuves de causalité. "
        "Elles distinguent les constats mesurés des limites de couverture."
    )

    latest_year = int(vehicules["annee"].max())
    registrations = vehicules.loc[vehicules["annee"] == latest_year].groupby("groupe")["valeur"].sum()
    registrations_total = int(registrations.sum())
    motorcycle_registrations = int(registrations.get("Deux-roues", 0))
    motorcycle_share = motorcycle_registrations / registrations_total * 100

    roads_by_bad_share = regions.sort_values("part_mauvais_pct", ascending=False)
    roads_by_bad_length = regions.sort_values("etat_mauvais_km", ascending=False)
    highest_bad_share = roads_by_bad_share.iloc[0]
    highest_bad_length = roads_by_bad_length.iloc[0]
    highest_work_length = regions.sort_values("etat_travaux_km", ascending=False).iloc[0]

    accident_change = accidents.set_index("annee")["accidents"].pct_change()
    large_changes = accident_change[accident_change.abs() > 0.5]
    missing_school_records = prefectures.loc[~prefectures["auto_ecoles_entree_presente"]]
    maritime_entries = int((auto_ecoles["region"] == "Maritime").sum())

    recommendations = [
        {
            "title": "Vérifier les ruptures et améliorer le codage des accidents",
            "priority": "Élevée",
            "reason": (
                "La série nationale présente des variations annuelles supérieures à 50 % en "
                + (", ".join(
                    f"{int(year)} ({value:+.0%})" for year, value in large_changes.items()
                ) if not large_changes.empty else "aucune année détectée par le seuil de 50 %")
                + ". Les accidents ne sont pas localisés par région/préfecture ni ventilés par véhicule."
            ),
            "data": "CSV accidents national, 2010-2022; champs accidents, blessés, morts.",
            "target": "Producteurs de statistiques routières; prochaine collecte nationale.",
            "action": "Documenter les changements de définition/couverture et publier une ventilation par territoire et type d’usager.",
            "limit": "Les variations peuvent refléter un changement réel ou une méthode de comptage; les données seules ne permettent pas de trancher.",
        },
        {
            "title": "Prioriser l’examen des tronçons en mauvais état",
            "priority": "Élevée pour l’expertise terrain",
            "reason": (
                f"En 2020, {highest_bad_share['region']} présente la plus forte part en mauvais état "
                f"({highest_bad_share['part_mauvais_pct']:.1f} %), tandis que {highest_bad_length['region']} "
                f"a le plus grand volume ({highest_bad_length['etat_mauvais_km']:.1f} km). "
                f"{highest_work_length['region']} a le plus de kilomètres classés en travaux "
                f"({highest_work_length['etat_travaux_km']:.1f} km)."
            ),
            "data": "État du réseau 2020; longueurs par état, agrégées pour routes revêtues et en terre.",
            "target": f"Services routiers de {highest_bad_share['region']} (part) et {highest_bad_length['region']} (volume), à confirmer sur le terrain.",
            "action": "Auditer les tronçons concernés et établir un programme d’entretien fondé sur inspection, trafic, coût et sécurité.",
            "limit": "Les données sont un seul millésime; 295 km sont attribués manuellement à une région et 11.1 km restent non attribués. Ni trafic ni coût n’est fourni.",
        },
        {
            "title": "Maintenir la prévention moto dans les actions nationales",
            "priority": "Moyenne, à confirmer par les données d’accidents par usager",
            "reason": (
                f"Les deux-roues représentent {motorcycle_share:.1f} % des {registrations_total:,} "
                f"immatriculations enregistrées en {latest_year} ({motorcycle_registrations:,} deux-roues)."
            ),
            "data": f"Immatriculations annuelles par catégorie, {latest_year}; accidents nationaux sans type de véhicule.",
            "target": "Usagers de deux-roues à l’échelle nationale, sans classement régional du risque.",
            "action": "Conserver des messages de prévention adaptés aux motos et mesurer les résultats avec des accidents ventilés par usager.",
            "limit": "Les immatriculations sont un flux annuel, pas le nombre de motos en circulation; les données ne prouvent pas que les motos causent une part donnée des accidents.",
        },
        {
            "title": "Auditer l’inventaire des auto-écoles avant d’ouvrir de nouveaux sites",
            "priority": "Moyenne",
            "reason": (
                f"Le fichier contient {len(auto_ecoles)} entrées, dont {maritime_entries} en Maritime; "
                f"{len(missing_school_records)} préfectures n’ont aucune entrée recensée."
            ),
            "data": "Points d’auto-écoles et statuts; date d’observation et exhaustivité non renseignées.",
            "target": "Préfectures sans entrée dans le fichier, après vérification locale de l’offre réelle.",
            "action": "Confirmer l’actualité et l’exhaustivité du registre, puis évaluer les distances d’accès à la formation.",
            "limit": "Aucune entrée du fichier ne signifie pas nécessairement absence de service; les ratios à la population 2022 ne sont pas temporellement vérifiés.",
        },
    ]

    for index, recommendation in enumerate(recommendations, start=1):
        st.markdown(f"### {index}. {recommendation['title']}")
        st.markdown(f"**Priorité :** {recommendation['priority']}")
        st.markdown(f"**Constat :** {recommendation['reason']}")
        st.markdown(f"**Indicateurs :** {recommendation['data']}")
        st.markdown(f"**Territoire/cible :** {recommendation['target']}")
        st.markdown(f"**Action :** {recommendation['action']}")
        st.markdown(f"**Limite :** {recommendation['limit']}")
        if index < len(recommendations):
            st.divider()
