import streamlit as st

from config import COLORS
from utils.components import data_limitation_box, render_header, section_title
from utils.data import get_data


def show_recommandations():
    data = get_data()
    vehicules = data["vehicules"]
    accidents = data["accidents"]
    regions = data["regions"]
    auto_ecoles = data["auto_ecoles"]
    prefectures = data["prefectures"]

    render_header()
    section_title("Recommandations stratégiques et opérationnelles", "Mesures ciblées fondées sur les indicateurs mesurés")

    st.markdown(
        """
        Les recommandations formulées ci-dessous découlent **directement des indicateurs chiffrés** calculés dans ce tableau de bord. 
        Conformément aux règles de déontologie des données : elles distinguent rigoureusement les **constats mesurés** 
        des **limites statistiques de couverture**, évitant toute généralité infondée.
        """
    )

    # Indicateurs dynamiques pour nourrir les recommandations
    latest_veh_y = int(vehicules["annee"].max())
    veh_latest = vehicules[vehicules["annee"] == latest_veh_y]
    immats_tot = int(veh_latest["valeur"].sum())
    motos_tot = int(veh_latest[veh_latest["groupe"] == "Deux-roues"]["valeur"].sum())
    part_motos = (motos_tot / immats_tot * 100) if immats_tot > 0 else 0

    acc_2022 = accidents[accidents["annee"] == 2022].iloc[0]
    total_acc = int(acc_2022["accidents"])
    total_morts = int(acc_2022["morts"])
    total_blesses = int(acc_2022["blesses"])

    reg_share_worst = regions.sort_values("part_mauvais_pct", ascending=False).iloc[0]
    reg_km_worst = regions.sort_values("etat_mauvais_km", ascending=False).iloc[0]
    reg_travaux_top = regions.sort_values("etat_travaux_km", ascending=False).iloc[0]

    tot_ae = len(auto_ecoles)
    ae_non_agreees = int((auto_ecoles["statut"] == "Non agréée").sum())
    part_non_agreees = (ae_non_agreees / tot_ae * 100) if tot_ae > 0 else 0
    pref_vides = prefectures[~prefectures["auto_ecoles_entree_presente"]]

    recommandations = [
        {
            "id": "1",
            "titre": "Combler le fossé de formation des deux-roues et prévenir la mortalité moto",
            "priorite": "Urgence Élevée",
            "badge_color": COLORS["danger"],
            "constat": (
                f"En {latest_veh_y}, les deux-roues représentent {part_motos:.1f}% des immatriculations annuelles "
                f"({motos_tot:,} motos sur {immats_tot:,} véhicules). Dans le même temps, seuls 4 837 permis moto (A) "
                f"ont été délivrés en 2022 (et moins de 1 000/an historiquement). "
                f"Le bilan d'insécurité routière culmine à {total_morts:,} décès et {total_blesses:,} blessés pour {total_acc:,} accidents."
            ).replace(",", " "),
            "indicateurs": f"CSV parc ({latest_veh_y}), CSV permis (catégorie A, 2022), CSV accidents (2022).",
            "territoire": "Échelle nationale, avec priorité aux grands bassins urbains (Grand Lomé / Maritime, Kara, Sokodé).",
            "actions": [
                "Lancer une campagne nationale de régularisation et de délivrance simplifiée du permis moto (A) à tarif social pour les conducteurs de taxi-motos (zémidjans).",
                "Rendre effectif et contrôler rigoureusement le port obligatoire du casque homologué (conducteur et passager).",
                "Intégrer des modules de sécurité routière et de secourisme d'urgence dans les cursus de formation des corporations de motocyclistes.",
            ],
            "limite": "Les immatriculations décrivent un flux annuel et non le parc roulant ; les données d'accidents ne ventilent pas les victimes par mode de transport.",
        },
        {
            "id": "2",
            "titre": "Régulariser les auto-écoles et désenclaver la formation dans les préfectures isolées",
            "priorite": "Priorité Moyenne à Forte",
            "badge_color": COLORS["accent_dark"],
            "constat": (
                f"Sur les {tot_ae} auto-écoles recensées, {ae_non_agreees} sont classées « Non agréée » (soit {part_non_agreees:.1f}% du parc). "
                f"De plus, {len(pref_vides)} préfectures ne disposent d'aucun établissement consigné dans le registre public, "
                f"alors que la région Maritime concentre la majorité écrasante des capacités de formation."
            ),
            "indicateurs": "CSV auto_ecoles (statuts d'agrément), CSV indicateurs_prefectures (taux / 100 000 hab).",
            "territoire": f"Préfectures de l'intérieur sans établissement enregistré ({', '.join(pref_vides['prefecture'].head(5))}...) et établissements non régularisés.",
            "actions": [
                "Mettre en place un guichet unique de régularisation avec accompagnement technique pour labelliser les auto-écoles non agréées répondant aux standards pédagogiques.",
                "Instaurer des incitations fiscales ou des bourses d'installation pour ouvrir des antennes d'auto-écoles agréées dans les chefs-lieux préfectoraux dépourvus.",
                "Développer des unités mobiles de formation et d'examen au permis de conduire dans les zones rurales éloignées.",
            ],
            "limite": "Le fichier source ne comporte pas de date d'observation ni de preuve d'exhaustivité ; une préfecture sans entrée dans le registre peut avoir des initiatives informelles.",
        },
        {
            "id": "3",
            "titre": "Plan d'entretien routier ciblé : Arbitrage entre part relative et volume kilométrique",
            "priorite": "Priorité Élevée d'investissement infrastructure",
            "badge_color": COLORS["primary"],
            "constat": (
                f"L'audit 2020 montre que {regions['etat_mauvais_km'].sum():.1f} km sont en mauvais état. "
                f"La région {reg_share_worst['region']} affiche la plus forte proportion de routes dégradées ({reg_share_worst['part_mauvais_pct']:.1f}%), "
                f"tandis que la région {reg_km_worst['region']} concentre le plus vaste linéaire dégradé absolu ({reg_km_worst['etat_mauvais_km']:.1f} km). "
                f"Par ailleurs, {regions['etat_travaux_km'].sum():.1f} km de tronçons étaient répertoriés en chantiers/travaux inachevés."
            ),
            "indicateurs": "CSV etat_routes (2020), CSV indicateurs_regions.",
            "territoire": f"Région {reg_km_worst['region']} (volume kilométrique prioritaire) et région {reg_share_worst['region']} (taux de dégradation prioritaire).",
            "actions": [
                f"Programmer en priorité les réfections structurelles sur les axes majeurs de la région {reg_km_worst['region']} pour préserver le réseau de connexion interurbaine.",
                f"Allouer un fonds spécial de réhabilitation ciblée pour la région {reg_share_worst['region']} afin de réduire son ratio critique de dégradation.",
                f"Auditer et accélérer l'achèvement des {regions['etat_travaux_km'].sum():.1f} km de chantiers en cours, dont le blocage pénalise la circulation.",
            ],
            "limite": "L'état du réseau est fondé sur le millésime 2020 unique ; le trafic journalier (TJA), la population directement desservie et le coût au km ne sont pas fournis.",
        },
        {
            "id": "4",
            "titre": "Moderniser la gouvernance des données : Territorialisation et interconnexion des systèmes",
            "priorite": "Recommandation Structurelle / Transversale",
            "badge_color": COLORS["blue"],
            "constat": (
                "L'analyse révèle des ruptures statistiques majeures (+154% d'accidents en 2011, +89% en 2016), "
                "une absence totale de localisation territoriale des accidents, un millésime routier figé à 2020, "
                "et des immatriculations non consolidées en stock de parc roulant actif."
            ),
            "indicateurs": "Ensemble des 7 fichiers du portail de données ouvertes.",
            "territoire": "Ministère des Transports, Direction des Transports Routiers (DTRF), Police, Gendarmerie, INSEED.",
            "actions": [
                "Généraliser le Bulletin d'Analyse des Accidents Corporels (BAAC) numérique et géolocalisé pour enregistrer précisément le lieu (coordonnées GPS), les usagers impliqués et les causes présumées.",
                "Actualiser annuellement l'audit d'état du réseau routier pour disposer d'un suivi dynamique pluriannuel de l'impact des investissements.",
                "Croiser les fichiers d'immatriculations avec le contrôle technique automobile pour estimer le parc roulant réel en circulation active.",
            ],
            "limite": "Nécessite une coordination interministérielle et un renforcement des capacités statistiques des brigades territoriales.",
        },
    ]

    for item in recommandations:
        st.markdown(
            f"""
            <div class="panel" style="margin-bottom: 1.5rem; border-left: 5px solid {item['badge_color']};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h3 style="margin: 0; color: #1a2728; font-size: 1.15rem;">
                        {item['id']}. {item['titre']}
                    </h3>
                    <span style="background: {item['badge_color']}18; color: {item['badge_color']}; font-weight: 700; font-size: 0.78rem; padding: 4px 10px; border-radius: 12px; border: 1px solid {item['badge_color']}40;">
                        {item['priorite']}
                    </span>
                </div>
                <div style="font-size: 0.88rem; line-height: 1.5; color: #2c3e40; margin-bottom: 0.6rem;">
                    <strong>Constat mesuré :</strong> {item['constat']}
                </div>
                <div style="font-size: 0.82rem; color: #5f6f73; margin-bottom: 0.6rem;">
                    <strong>Indicateurs sources :</strong> <code>{item['indicateurs']}</code> · <strong>Territoire cible :</strong> {item['territoire']}
                </div>
                <div style="background: #ffffff; border-radius: 8px; padding: 0.8rem 1rem; border: 1px solid #e2ece7; margin-bottom: 0.6rem;">
                    <strong style="color: #0a614e; font-size: 0.85rem;">Plan d'action opérationnel :</strong>
                    <ul style="margin: 0.3rem 0 0 0; padding-left: 1.2rem; font-size: 0.84rem; color: #2b3e42;">
                        {''.join(f'<li>{act}</li>' for act in item['actions'])}
                    </ul>
                </div>
                <div style="font-size: 0.78rem; color: #7a8c8f; font-style: italic;">
                    <strong>Limite méthodologique :</strong> {item['limite']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    data_limitation_box(
        "Toutes les recommandations sont ancrées dans la réalité des chiffres disponibles. "
        "Elles n'extrapolent pas au-delà des indicateurs calculés et signalent explicitement les limites "
        "de chaque jeu de données source pour éclairer au mieux la prise de décision publique.",
        title="Périmètre de décision publique responsable"
    )

