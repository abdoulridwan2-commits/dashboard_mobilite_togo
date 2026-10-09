# Mobilité et sécurité routière au Togo

Tableau de bord interactif développé en Python (Streamlit) pour le **Data Challenges Togo AI Lab, Défi 1 : Administration territoriale et mobilité**.

## Contexte

Le nombre de véhicules immatriculés chaque année au Togo a plus que quadruplé en vingt ans, porté par les motos. Dans le même temps, les accidents de la route augmentent : plus de 7 500 accidents et 683 morts en 2022. Le réseau routier reste inégalement entretenu selon les régions.

Ce projet exploite les données ouvertes disponibles pour mesurer l'évolution de la mobilité et de la sécurité routière, puis proposer des recommandations pour une mobilité plus sûre.

## Objectifs

- Retracer l'évolution des véhicules immatriculés (voitures, motos, poids lourds) et des permis de conduire délivrés par catégorie.
- Analyser la sécurité routière : accidents, blessés et morts, rapportés à la population et au nombre de véhicules.
- Évaluer l'état du réseau routier par tronçon et par région : bon état, état moyen, mauvais état, travaux en cours.
- Cartographier le réseau routier classé et les auto-écoles par région et par préfecture, et les rapporter à la population.
- Proposer des recommandations ciblées pour améliorer la sécurité routière, la formation des conducteurs et l'entretien du réseau dans les régions les moins bien desservies.

## Pages du tableau de bord

| Page                 | Contenu                                                                                          |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| Vue d'ensemble       | Indicateurs datés, flux annuels d'immatriculations, filtres de période et constats calculés      |
| Objectifs            | Périmètre réellement disponible et limites d'interprétation                                      |
| Véhicules & Permis   | Courbes filtrables par catégorie; comparaison en indice base 100 sur période commune             |
| Accidents & Sécurité | Comptes nationaux séparés; taux par habitant calculés uniquement en 2022                         |
| Réseau routier       | État 2020 filtrable par région et type, kilomètres et parts séparés                              |
| Cartographie         | Géométries des routes classées et points d'auto-écoles filtrables par région/préfecture          |
| Auto-écoles          | Entrées du registre, statuts et filtre territorial; absences signalées comme non-enregistrements |
| Recommandations      | Actions avec constats, indicateurs, cible, priorité et limites                                   |

## Données

Les données proviennent du portail de données ouvertes du Togo. Les fichiers bruts sont dans `data/raw/`.

| Fichier                | Contenu                                   | Niveau géographique         |
| ---------------------- | ----------------------------------------- | --------------------------- |
| `parc_vehicules.csv`   | Véhicules immatriculés par type           | National                    |
| `permis.csv`           | Permis de conduire délivrés par catégorie | National                    |
| `accidents_trafic.csv` | Accidents, blessés, morts                 | National                    |
| `etat_routes.csv`      | État des routes par tronçon (2020)        | Tronçon                     |
| `population.csv`       | Population 2022                           | Région, préfecture, commune |
| `routes_classees.csv`  | Tracés du réseau routier classé           | Région, préfecture          |
| `auto_ecoles.csv`      | Auto-écoles géolocalisées                 | Région, préfecture          |

### Limites connues

- Les accidents, immatriculations et permis sont nationaux; aucun taux d'accidents par région/préfecture n'est calculable.
- Les immatriculations sont des flux annuels et ne constituent pas un stock de véhicules en circulation. Aucun taux d'accidents par véhicule n'est affiché.
- La population n'est connue par recensement que pour 2022; les taux de mortalité et de blessés par habitant ne sont calculés que pour 2022.
- L'état routier ne couvre que 2020. Environ 295 km sont attribués manuellement à une région et environ 11 km restent non attribués; ces derniers sont exclus des proportions régionales.
- Les auto-écoles sont géolocalisées, mais leur fichier ne précise ni millésime ni exhaustivité. Une préfecture sans entrée n'est pas déclarée dépourvue de service.
- Les ratios d'auto-écoles utilisent la population du recensement 2022 avec un inventaire non daté : ils sont descriptifs et leur comparabilité temporelle n'est pas vérifiée.
- Les ratios routiers sont des kilomètres par habitant, pas une densité par superficie (les superficies territoriales ne sont pas fournies).
- Le libellé source « Accidents mortels /100.000 hab » est ambigu; il est conservé comme taux source séparé et ne sert pas à reconstruire les populations historiques.
- L'année 2013 n'a aucune valeur par catégorie de permis; elle reste vide et n'est pas traitée comme zéro.
- Les fichiers bruts du dépôt ne contiennent pas les URL sources par fichier ni les dates d'extraction. Ces métadonnées doivent être ajoutées dès qu'elles sont récupérées du portail.

## Installation

Prérequis : Python 3.10 ou plus récent.

```bash
git clone https://github.com/abdoulridwan2-commits/dashboard_mobilite_togo.git
cd dashboard-mobilite-securite-togo

python -m venv venv
```

Activation de l'environnement :

```bash
# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux / Mac
source venv/bin/activate
```

Installation des dépendances et lancement :

```bash
pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

## Structure du projet

```
dashboard-mobilite-securite-routiere-togo/
├── app.py                 # Point d'entrée et navigation
├── config.py              # Titre, couleurs, liste des filtres
├── requirements.txt
├── assets/                # Logo et image du bandeau
├── data/
│   ├── raw/               # Données d'origine
│   └── processed/         # Données nettoyées
├── scripts/
│   └── nettoyage.py       # Nettoyage et préparation des données
├── utils/
│   ├── style.py           # Feuille de style (CSS)
│   ├── components.py      # Bandeau, navigation, cartes et pied de page
│   └── data.py            # Chargement des données
└── views/                 # Une page par entrée de la barre latérale
```

## Technologies

Python, Streamlit, pandas, Plotly, GeoPandas, Folium.

## Méthodologie

- Le rapport reproductible `data/processed/rapport_qualite.txt` est généré par `python scripts/nettoyage.py`.
- Les taux par habitant en sécurité routière utilisent le recensement 2022 : nombre de morts ou de blessés / 8 095 498 habitants × 100 000.
- Le ratio morts / 100 accidents est un quotient brut : morts / accidents × 100; il ne s'agit pas d'un taux de mortalité des personnes accidentées.
- Les parts d'état routier sont calculées par longueur : kilomètres d'un état / kilomètres d'état connus × 100.
- L'indice base 100 des véhicules et permis compare uniquement leurs variations, pas leurs volumes, et ne démontre pas de relation causale.
- Les changements d'accidents supérieurs à 50 % en 2011 et 2016 sont signalés comme ruptures à vérifier, sans conclure à leur cause.

## État d'avancement

Le dashboard, les vues principales, les filtres de période/territoire, la carte et le rapport qualité sont implémentés. Les métadonnées de provenance détaillées et l'historique de l'état routier restent à obtenir; les accidents par territoire et le parc roulant ne sont pas présents dans les fichiers actuels.

## Auteur

Dashboard réalisé par **Abdoulaye Ridwan**, dans le cadre du Togo AI Lab.
