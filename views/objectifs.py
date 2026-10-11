from pathlib import Path
import streamlit as st

from utils.components import data_limitation_box, render_header, section_title


def show_objectifs():
    render_header()

    section_title("Contexte et problématique du défi", "Togo AI Lab · Défi 1 : Administration territoriale et mobilité")

    st.markdown(
        """
        Le nombre de véhicules immatriculés chaque année au Togo a **plus que quadruplé en vingt ans**, 
        porté principalement par l'explosion des **motos et deux-roues**. 
        Dans le même temps, les accidents de la circulation augmentent : plus de **7 500 accidents et 683 morts en 2022**. 
        Par ailleurs, le réseau routier reste inégalement entretenu selon les régions, et l'accès à la formation à la conduite 
        présente de fortes disparités territoriales.

        À partir des 7 jeux de données ouvertes mis à disposition, ce tableau de bord analyse l'évolution de la mobilité et de la sécurité routière, 
        mesure l'état des infrastructures et propose des **recommandations opérationnelles et ciblées** pour une mobilité plus sûre et durable au Togo.
        """
    )

    st.markdown("### 🎯 Les 5 Objectifs du Défi")
    obj_c1, obj_c2 = st.columns(2)

    with obj_c1:
        st.markdown(
            """
            1. **Mobilité & Parc roulant :** Analyser l'évolution des immatriculations annuelles (voitures, motos, poids lourds) et des permis délivrés par catégorie (A à F).
            2. **Sécurité routière :** Mesurer les accidents, blessés et décès, les rapporter à la population de référence et analyser les indices de létalité.
            3. **État du réseau routier :** Dresser l'état des lieux du réseau classé en 2020 par tronçon et par région (bon état, état moyen, mauvais état, travaux).
            """
        )

    with obj_c2:
        st.markdown(
            """
            4. **Cartographie interactive :** Cartographier le réseau routier classé et les auto-écoles par région et préfecture, et calculer les ratios d'équipements par rapport à la population.
            5. **Recommandations fondées sur les données :** Formuler des préconisations concrètes pour la sécurité routière, la formation des usagers et l'entretien ciblé du réseau dans les territoires les plus vulnérables.
            """
        )

    st.markdown("### 📁 Périmètre des données ouvertes (7 fichiers bruts)")
    st.markdown(
        """
        | Fichier source | Données contenues | Période couverte | Échelle géographique |
        | :--- | :--- | :--- | :--- |
        | `parc_vehicules.csv` | Immatriculations annuelles de véhicules par type | 1990 – 2022 | Nationale |
        | `permis.csv` | Permis de conduire délivrés par catégorie (A à F) | 2007 – 2022 | Nationale |
        | `accidents_trafic.csv` | Accidents corporels, blessés, morts | 2010 – 2022 | Nationale |
        | `etat_routes.csv` | État d'entretien du réseau par tronçon (km) | 2020 uniquement | Tronçon routier |
        | `population.csv` | Recensement Général de la Population et de l'Habitat | 2022 (RGPH-5) | Région, préfecture, commune |
        | `routes_classees.csv` | Tracés géométriques WKT des routes classées | Inventaire | Région, préfecture |
        | `auto_ecoles.csv` | Établissements d'auto-écoles (points WKT, agrément) | Registre | Région, préfecture |
        """
    )

    st.markdown("### ⚙️ Traitement rigoureux des pièges connus")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            """
            - **Exclusion des lignes « Total » :** Les lignes de somme globale dans le parc, les permis et l'état des routes (dont `TOTAL RT`) sont systématiquement exclues des agrégations pour bannir tout double comptage.
            - **Permis 2013 manquant :** En 2013, la source affiche 0 pour le total sans détail par catégorie. L'année est laissée vide (`NaN`) et n'est pas faussée en 0.
            - **Correction du libellé d'accidentologie :** Le champ source *« Accidents mortels /100.000 hab »* correspond en réalité au taux de l'ensemble des accidents rapporté à la population (92,73 en 2022).
            """
        )
    with p2:
        st.markdown(
            """
            - **Cohérence territoriale Lomé / Maritime :** Le recensement sépare le Grand Lomé (DAGL : Golfe et Agoè-Nyivé) de la Maritime, alors que les fichiers routes et auto-écoles les regroupent. Population Maritime = Maritime + DAGL (3 534 991 hab).
            - **Préfecture de Mô & Normalisation :** Mô (Centrale) absente des fichiers géographiques est réintégrée pour égaler la population régionale. Les noms de préfectures sont unifiés sans accents ni casses hétérogènes.
            - **Abandon du niveau commune :** En raison d'incohérences de désignation entre fichiers, les analyses sont fiabilisées au niveau préfectoral et régional.
            """
        )

    # Affichage du rapport de qualité des données
    with st.expander("📄 Consulter le rapport de qualité des données généré par le script de nettoyage", expanded=False):
        rep_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "rapport_qualite.txt"
        if rep_path.exists():
            st.code(rep_path.read_text(encoding="utf-8"), language="text")
        else:
            st.info("Le rapport de qualité est consultable dans `data/processed/rapport_qualite.txt`.")

    data_limitation_box(
        "Ce tableau de bord repose exclusivement sur les données officielles fournies. "
        "En conformité avec les règles du défi : aucune donnée n'a été inventée. "
        "Les limites statistiques (accidents uniquement nationaux, état des routes limité à 2020, "
        "immatriculations constituant un flux annuel et non un parc roulant) sont clairement affichées sur chaque vue.",
        title="Charte d'intégrité et de transparence"
    )

