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

| Page                 | Contenu                                                                     |
| -------------------- | --------------------------------------------------------------------------- |
| Vue d'ensemble       | Indicateurs clés : immatriculations, accidents, état du réseau, auto-écoles |
| Objectifs            | Objectifs du défi                                                           |
| Véhicules & Permis   | Parc de véhicules par type et permis délivrés par catégorie                 |
| Accidents & Sécurité | Accidents, blessés et morts, rapportés à la population et aux véhicules     |
| Réseau routier       | État du réseau par région et par tronçon                                    |
| Cartographie         | Réseau routier classé et auto-écoles par région et préfecture               |
| Auto-écoles          | Répartition des auto-écoles et rapport à la population                      |
| Recommandations      | Pistes d'action par région                                                  |

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

- Les accidents, les véhicules et les permis sont disponibles uniquement au niveau national : aucun indicateur d'accidents par région n'est calculable.
- L'état du réseau routier ne couvre que l'année 2020.
- Dans les données de population, Lomé (Golfe et Agoè-Nyivé) est séparé de la région Maritime, alors que les auto-écoles de Lomé sont classées dans la Maritime. Le calcul des ratios par habitant doit en tenir compte.
- Les noms de régions et de préfectures diffèrent d'un fichier à l'autre (accents, majuscules) et doivent être normalisés avant les jointures.

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
│   ├── components.py      # Bandeau, filtres, cartes, pied de page
│   └── data.py            # Chargement des données
└── views/                 # Une page par entrée de la barre latérale
```

## Technologies

Python, Streamlit, pandas, Plotly, GeoPandas, Folium.

## Avancement

- [x] Structure du projet et maquette de l'interface
- [ ] Nettoyage et harmonisation des données
- [ ] Page Véhicules & Permis
- [ ] Page Accidents & Sécurité
- [ ] Page Réseau routier
- [ ] Cartographie et page Auto-écoles
- [ ] Recommandations

## Auteur

Dashboard réalisé par **Abdoulaye Ridwan**, dans le cadre du Togo AI Lab.
