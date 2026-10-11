# Rapport Méthodologique et Analytique
## Défi 1 : Administration territoriale et mobilité — Togo AI Lab (Data Challenges)

**Auteur :** Abdoulaye Ridwan  
**Projet :** Tableau de bord interactif de la mobilité et de la sécurité routière au Togo  
**Technologies :** Python, Streamlit, pandas, Plotly, GeoPandas, Folium  
**Date :** 2024  

---

## Sommaire

1. [Contexte et Problématique](#1-contexte-et-problématique)
2. [Périmètre et Description des Données Ouvertes](#2-périmètre-et-description-des-données-ouvertes)
3. [Méthodologie de Nettoyage et Traitement des Pièges Statistiques](#3-méthodologie-de-nettoyage-et-traitement-des-pièges-statistiques)
4. [Définition des Indicateurs et Formules de Calcul](#4-définition-des-indicateurs-et-formules-de-calcul)
5. [Résultats et Analyses Approfondies par Axe](#5-résultats-et-analyses-approfondies-par-axe)
   - [5.1 Mobilité & Parc : L'envolée des deux-roues et le déficit de permis A](#51-mobilité--parc--lenvolée-des-deux-roues-et-le-déficit-de-permis-a)
   - [5.2 Sécurité Routière : Comptes nationaux, gravité et ruptures de séries](#52-sécurité-routière--comptes-nationaux-gravité-et-ruptures-de-séries)
   - [5.3 État du Réseau Routier : Double lecture part relative vs volume kilométrique](#53-état-du-réseau-routier--double-lecture-part-relative-vs-volume-kilométrique)
   - [5.4 Aménagement Territorial & Auto-écoles : Disparités d'accès à la formation](#54-aménagement-territorial--auto-écoles--disparités-daccès-à-la-formation)
6. [Recommandations Stratégiques et Opérationnelles](#6-recommandations-stratégiques-et-opérationnelles)
7. [Limites Méthodologiques et Perspectives pour les Futures Collectes](#7-limites-méthodologiques-et-perspectives-pour-les-futures-collectes)

---

## 1. Contexte et Problématique

Au cours des deux dernières décennies, la République Togolaise a connu une mutation profonde de ses dynamiques de transport. Le volume annuel de véhicules immatriculés a plus que quadruplé en vingt ans, tiré de façon prépondérante par l'essor spectaculaire des deux-roues motorisés (motos), devenus le mode de déplacement individuel et commercial (taxis-motos ou *zémidjans*) prédominant dans les agglomérations comme en milieu rural.

Parallèlement à cette motorisation accélérée, l'insécurité routière s'est aggravée pour atteindre un bilan critique : en 2022, les statistiques officielles font état de plus de **7 500 accidents de la circulation corporels**, causant **9 918 blessés** et **683 décès**, soit une moyenne de près de deux morts par jour sur les axes togolais.

À ces enjeux humains et sanitaires s'ajoutent des disparités territoriales d'infrastructures : le réseau routier classé présente un état d'entretien contrasté selon les régions administratives (Centrale, Kara, Maritime, Plateaux, Savanes), tandis que les structures de formation des conducteurs (auto-écoles) demeurent fortement concentrées dans la zone littorale et la capitale.

L'objectif de ce travail est de concevoir un tableau de bord décisionnel rigoureux, ergonomique et reproductible permettant d'évaluer objectivement l'état de la mobilité et de la sécurité routière au Togo, sans inventer de données, et de formuler des préconisations d'action publique fondées sur des preuves chiffrées.

---

## 2. Périmètre et Description des Données Ouvertes

L'analyse repose sur l'exploitation de 7 jeux de données ouverts mis à disposition dans le répertoire `data/raw/` :

| Fichier source | Description du contenu | Horizon temporel | Granularité spatiale | Variables maîtresses |
| :--- | :--- | :--- | :--- | :--- |
| `parc_vehicules.csv` | Immatriculations annuelles enregistrées par type de véhicule | 1990 – 2022 (33 ans) | Nationale | `Date` (année), `types-de-vehicule`, `Value` (nombre) |
| `permis.csv` | Permis de conduire officiellement délivrés par catégorie | 2007 – 2022 (16 ans) | Nationale | `Date` (année), `categories-de-permis` (A à F), `Value` |
| `accidents_trafic.csv` | Accidents corporels, personnes tuées et personnes blessées | 2010 – 2022 (13 ans) | Nationale | `Date` (année), `indicateur`, `Value` (effectif / taux) |
| `etat_routes.csv` | Diagnostic d'état de viabilité du réseau routier par tronçon | 2020 uniquement | Tronçon routier | `tronçon`, `indicateur` (revêtue/terre), `etat`, `Value` (km) |
| `population.csv` | Résultats du 5ᵉ Recensement Général de la Population (RGPH-5) | 2022 | Région, préfecture, commune | `découpage-administratif`, `Value` (nombre d'habitants) |
| `routes_classees.csv` | Linéaires et géométries des routes classées | Inventaire de référence | Région, préfecture | `geometry` (WKT), `route_nom`, `route_type`, `route_recouvrement` |
| `auto_ecoles.csv` | Répertoire géolocalisé des établissements d'enseignement de la conduite | Registre | Région, préfecture | `geometry` (POINT WKT), `nom_etablissement`, `agregation` (statut) |

---

## 3. Méthodologie de Nettoyage et Traitement des Pièges Statistiques

La manipulation de données administratives réelles impose un nettoyage systématique et documenté. Le script `scripts/nettoyage.py` a été développé pour automatiser ce processus et générer le rapport de contrôle d'intégrité `data/processed/rapport_qualite.txt`. Les règles suivantes ont été scrupuleusement appliquées :

### 3.1 Élimination des doubles comptes (Lignes « Total »)
Dans les fichiers `parc_vehicules.csv`, `permis.csv` et `etat_routes.csv`, des lignes récapitulatives « Total » (et « TOTAL RT ») figuraient au même niveau hiérarchique que les catégories individuelles. Les inclure dans les calculs aurait exactement doublé les sommes. Ces lignes ont été extraites à des fins exclusives de contrôle arithmétique (somme des modalités = total source), puis systématiquement exclues des tables de données traitées.

### 3.2 Traitement des données manquantes pour les permis en 2013
Pour l'année 2013, le fichier `permis.csv` affiche un total nul sans aucune ventilation par catégorie. Remplacer ces données par zéro aurait faussé les moyennes et suggéré qu'aucun permis n'avait été délivré au Togo en 2013. Les cellules correspondantes sont strictement encodées en valeurs manquantes (`NaN`) et connectées de façon discontinue sur les graphiques.

### 3.3 Correction de l'ambiguïté du taux d'accidents source
Dans `accidents_trafic.csv`, un indicateur était intitulé *« Accidents mortels /100.000 hab »*, affichant une valeur de 92,73 pour l'année 2022.  
Or, le recoupement arithmétique avec la population officielle du RGPH-5 2022 (8 095 498 habitants) établit :
$$\frac{7\,518 \text{ accidents}}{8\,095\,498 \text{ habitants}} \times 100\,000 = 92{,}86 \approx 92{,}73$$
Cet indicateur mesure donc **l'ensemble des accidents corporels pour 100 000 habitants**, et non les seuls accidents mortels (qui ne s'élèvent qu'à 8,44 décès pour 100 000 habitants). Le libellé a été corrigé pour prévenir toute interprétation erronée.

### 3.4 Réconciliation territoriale : Région Maritime et Grand Lomé (DAGL)
Le recensement de la population de 2022 distingue administrativement le District Autonome du Grand Lomé (DAGL : préfectures du Golfe et d'Agoè-Nyivé, 2 188 376 hab.) du reste de la région Maritime (1 346 615 hab.). À l'inverse, les bases de données des routes classées et des auto-écoles rattachent Golfe et Agoè-Nyivé directement à la région Maritime.  
Pour rendre les ratios par habitant strictement comparables, la population de la région Maritime a été consolidée selon la formule :
$$\text{Population Maritime} = \text{Maritime} + \text{DAGL} = 3\,534\,991 \text{ habitants}$$
La somme des 5 régions reconstituées (Maritime, Plateaux, Centrale, Kara, Savanes) égale exactement les 8 095 498 habitants du Togo.

### 3.5 Normalisation toponymique et préfecture de Mô
La préfecture de Mô (région Centrale), créée par réorganisation territoriale, est présente dans le recensement mais absente des fichiers géographiques des routes et des auto-écoles. Elle a été réintégrée explicitement avec une population de 45 422 habitants pour garantir l'exhaustivité territoriale de la région Centrale (795 529 habitants).  
Une fonction de normalisation a uniformisé l'ensemble des toponymes (suppression des accents, majuscules, tirets et espaces superflus).

### 3.6 Abandon de l'échelon communal
Les découpages communaux présentaient des incohérences majeures de désignation d'un fichier à l'autre (ex. « Amou 3 », « Binah 2 », « Danyi 1+Danyi 2 »). Pour éviter des regroupements erronés, le niveau d'agrégation géographique a été fiabilisé exclusivement aux échelons préfectoral (39 préfectures) et régional (5 régions).

### 3.7 Déduction régionale des tronçons du réseau routier
Le fichier `etat_routes.csv` ne comportait aucune colonne de région. La région a été déduite selon une hiérarchie stricte :
1. Code préfixe du tronçon : `TGRK` = Kara, `TGRP` = Plateaux, `TGRC` = Centrale, `TGRS` = Savanes, `TGRM` = Maritime ;
2. Attribution manuelle documentée pour 7 tronçons historiques (295 km rattachés à la Maritime) ;
3. Recoupement toponymique avec les routes classées ;
4. Marquage transparent des 11,1 km non attribués (tronçon ALINMONDJI (RN1)-ELAVAGNON), exclus des pourcentages régionaux pour ne pas biaiser les parts relatives.

---

## 4. Définition des Indicateurs et Formules de Calcul

Afin d'assurer la comparabilité scientifique des analyses, les indicateurs suivants ont été modélisés :

### 4.1 Taux de sécurité routière rapportés à la population (2022)
Calculés exclusivement sur l'année de recensement 2022 ($P_{2022} = 8\,095\,498$) :
$$\text{Taux d'accidents pour } 100\,000 \text{ hab.} = \frac{\text{Accidents}_{2022}}{P_{2022}} \times 100\,000 = \frac{7\,518}{8\,095\,498} \times 100\,000 \approx 92{,}86$$
$$\text{Taux de mortalité routière pour } 100\,000 \text{ hab.} = \frac{\text{Morts}_{2022}}{P_{2022}} \times 100\,000 = \frac{683}{8\,095\,498} \times 100\,000 \approx 8{,}44$$
$$\text{Taux de morbidité (blessés) pour } 100\,000 \text{ hab.} = \frac{\text{Blessés}_{2022}}{P_{2022}} \times 100\,000 = \frac{9\,918}{8\,095\,498} \times 100\,000 \approx 122{,}51$$

### 4.2 Indice de létalité relative des accidents
Quotient brut mesurant la sévérité moyenne des sinistres corporels recensés :
$$\text{Létalité relative (\%)} = \frac{\text{Nombre de morts}}{\text{Nombre d'accidents}} \times 100$$
En 2022, cet indice s'élève à $\frac{683}{7\,518} \times 100 \approx 9{,}08\%$, soit environ 9 personnes tuées pour 100 accidents enregistrés.

### 4.3 Parts relatives d'état du réseau routier
Pour une région donnée $r$ et un état $e \in \{\text{bon}, \text{moyen}, \text{mauvais}, \text{travaux}\}$ :
$$\text{Part de l'état } e \text{ (\%)} = \frac{\text{Longueur en état } e \text{ (km)}}{\text{Longueur totale évaluée dans la région (km)}} \times 100$$

### 4.4 Ratios d'équipement territorial
- **Desserte routière classée :** $\frac{\text{Longueur de routes (km)}}{\text{Population}} \times 1\,000$ (en kilomètres de route pour 1 000 habitants).
- **Densité d'auto-écoles :** $\frac{\text{Nombre d'auto-écoles}}{\text{Population}} \times 100\,000$ (en établissements répertoriés pour 100 000 habitants).

### 4.5 Indice comparatif en Base 100
Pour comparer les trajectoires relatives de deux séries $X_t$ (ex. immatriculations de motos) et $Y_t$ (ex. permis moto A) sur la période commune sans que les différences d'échelle ne masquent les tendances :
$$I_t(X) = \frac{X_t}{X_{t_0}} \times 100 \quad \text{où } t_0 \text{ est l'année initiale commune de référence.}$$

---

## 5. Résultats et Analyses Approfondies par Axe

### 5.1 Mobilité & Parc : L'envolée des deux-roues et le déficit de permis A

1. **Une motorisation portée par les motos :**  
   Les nouvelles immatriculations annuelles sont passées de moins de 15 000 au début des années 2000 à plus de 63 000 en 2022. Cette expansion est quasi-exclusivement portée par les **deux-roues et assimilés**, qui constituent plus de **71 % du flux d'immatriculations en 2022** (soit plus de 45 000 motos immatriculées sur l'année). Les voitures particulières et camionnettes représentent environ 20 % des flux, tandis que les poids lourds et véhicules de transport en commun forment le solde.

2. **Le gouffre structurel de la formation :**  
   Alors que plus de 40 000 à 45 000 motos entrent en circulation chaque année, le nombre de permis de conduire de catégorie A (motos) délivrés est resté historiquement très bas : souvent inférieur à 1 000 permis par an durant la décennie 2010. Malgré un sursaut en 2022 (4 837 permis A délivrés), **moins de 11 % des nouveaux conducteurs de deux-roues obtiennent un permis officiel la même année**.  
   Ce décalage confirme l'existence d'une pratique massive de conduite sans titre officiel ni formation certifiée, particulièrement dans le secteur informel des taxis-motos (*zémidjans*).

### 5.2 Sécurité Routière : Comptes nationaux, gravité et ruptures de séries

1. **Un tribut humain lourd et croissant :**  
   Entre 2010 et 2022, les accidents sont passés de 2 153 à 7 518 cas, les blessés de 3 440 à 9 918 personnes, et les décès de 333 à 683 morts. Avec un taux de mortalité de 8,44 décès pour 100 000 habitants en 2022 et près de 10 personnes tuées pour 100 accidents corporels, la route demeure l'une des causes majeures de morbidité évitable au Togo.

2. **Ruptures statistiques de 2011 et 2016 :**  
   L'analyse en variations annuelles révèle deux sauts majeurs :
   - En 2011 : **+154 % d'accidents** (passage de 2 153 à 5 464 cas) ;
   - En 2016 : **+89 % d'accidents** (passage de 4 821 à 9 104 cas).  
   Ces ruptures résultent vraisemblablement de modifications dans la couverture du recueil statistique (extension géographique des brigades de gendarmerie et commissariats déclarants) plutôt que d'un changement comportemental instantané.

### 5.3 État du Réseau Routier : Double lecture part relative vs volume kilométrique

L'analyse de l'audit 2020 (couvrant 3 373 km de routes revêtues et en terre) met en évidence l'importance de distinguer deux indicateurs :
1. **La proportion de dégradation (%) :**  
   La région **Centrale** et la région des **Savanes** enregistrent des taux relatifs élevés de réseau en mauvais état (dépassant 30 à 35 % de leur linéaire respectif).
2. **Le volume kilométrique dégradé (km absolus) :**  
   La région des **Plateaux** concentre à elle seule le plus vaste linéaire dégradé en valeur absolue (plus de 350 km en mauvais état), en raison de l'étendue de son réseau.
3. **Les chantiers en suspens :**  
   Plus de **270 km de réseau** étaient recensés sous le statut « Travaux en cours » en 2020. Le retard de livraison de ces chantiers aggrave la dangerosité et le ralentissement des flux économiques interurbains.

### 5.4 Aménagement Territorial & Auto-écoles : Disparités d'accès à la formation

1. **Précarité juridique du secteur :**  
   Sur les 272 établissements recensés dans le fichier national, **138 sont classés « Non agréée » (50,7 %)**, 85 sont « Agréée », 47 sont des « Antennes agréées », et 2 sont non renseignés. Plus de la moitié des auto-écoles exercent donc sans agrément formel vérifié.

2. **Fracture spatiale littorale vs intérieur :**  
   La région Maritime (incluant le Grand Lomé) concentre plus de 70 % des auto-écoles répertoriées. À l'opposé, plusieurs préfectures de l'intérieur (notamment dans les régions Centrale, Kara et Savanes) ne comptent qu'un seul établissement, voire aucun enregistré dans le registre (ex. préfecture de Mô).  
   Cette pénurie géographique pénalise l'accès régulier à une formation de qualité pour les populations éloignées de la capitale.

---

## 6. Recommandations Stratégiques et Opérationnelles

Les recommandations suivantes découlent directement des indicateurs calculés et respectent le cadre des données disponibles :

| N° | Axe d'intervention | Priorité | Constat chiffré source | Plan d'action opérationnel préconisé |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Sécurité des deux-roues & Permis A** | **Urgence Élevée** | ~45 000 motos/an vs ~4 800 permis A/an ; 683 morts en 2022. | • Lancer une opération nationale de délivrance simplifiée du permis A à tarif social pour les conducteurs de taxi-motos.<br>• Rendre rigoureusement obligatoire le port du casque homologué conducteur/passager.<br>• Former les associations de conducteurs aux gestes de premiers secours. |
| **2** | **Mise à niveau et déconcentration des auto-écoles** | **Priorité Forte** | 50,7 % d'écoles non agréées ; plusieurs préfectures à 0 entrée enregistrée. | • Ouvrir un guichet de régularisation et d'accompagnement aux normes pédagogiques des établissements non agréés.<br>• Inciter à l'ouverture d'antennes agréées dans les chefs-lieux préfectoraux non desservis via des exonérations temporaires.<br>• Déployer des unités mobiles d'examen du permis dans les zones rurales. |
| **3** | **Maintenance ciblée des infrastructures routières** | **Priorité Élevée d'investissement** | 1 037 km dégradés ; Plateaux = max km dégradés ; Centrale/Savanes = fort % dégradé. | • Arbitrer les crédits : réfection prioritaire des axes lourds de transport dans les Plateaux et réhabilitation ciblée des tronçons critiques en Centrale/Savanes.<br>• Conclure prioritairement les 272 km de chantiers répertoriés « en travaux » en 2020. |
| **4** | **Gouvernance et modernisation des données** | **Recommandation Structurelle** | Accidents 100% nationaux non spatialisés ; millésime routier figé à 2020. | • Généraliser le Bulletin d'Analyse des Accidents Corporels (BAAC) numérisé et géolocalisé par GPS.<br>• Actualiser périodiquement l'audit de viabilité du réseau routier.<br>• Interconnecter le fichier des immatriculations avec le contrôle technique pour estimer le stock roulant réel. |

---

## 7. Limites Méthodologiques et Perspectives pour les Futures Collectes

En application des directives éthiques du Togo AI Lab, les limites suivantes doivent être gardées à l'esprit lors de l'exploitation des résultats :

1. **Absence de localisation géographique des accidents :**  
   Les accidents, morts et blessés ne sont documentés qu'à l'échelle nationale. Aucune carte régionale ou préfectorale de l'accidentologie ne peut être construite sans extrapolations fallacieuses.
2. **Flux d'immatriculations vs Stock roulant réel :**  
   Les données du parc représentent un flux annuel de premières immatriculations (nouvelles cartes grises) et non le parc cumulé en circulation active (qui subit l'amortissement, les rebuts et les pannes). Aucun taux d'accidents rapporté au nombre de véhicules en circulation ne peut être calculé rigoureusement.
3. **Instantanéité temporelle de l'état routier (2020) :**  
   L'état des routes correspond à une photographie unique réalisée en 2020. Aucune dynamique temporelle (amélioration ou dégradation récente) ne peut en être déduite sans nouvelle collecte.
4. **Nature déclarative du registre des auto-écoles :**  
   Le fichier ne renseigne ni date d'observation ni garantie d'exhaustivité. L'absence d'établissement consigné dans une préfecture traduit l'absence de ligne dans le jeu de données administratif, et non la preuve matérielle d'une absence absolue d'initiatives de formation locale.

---

*Rapport rédigé par Abdoulaye Ridwan dans le cadre du défi Data Challenges – Togo AI Lab.*
