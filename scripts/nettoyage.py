"""
Nettoyage des données du défi « Mobilité et sécurité routière au Togo ».

Lancer depuis la racine du projet, environnement virtuel activé :
    python scripts/nettoyage.py

Lit les fichiers de data/raw/ et écrit dans data/processed/ :
    parc_vehicules.csv, permis.csv, accidents_national.csv,
    autres_indicateurs_nationaux.csv, etat_routes.csv,
    population_prefectures.csv, routes_classees.csv, auto_ecoles.csv,
    indicateurs_regions.csv, indicateurs_prefectures.csv,
    rapport_qualite.txt
"""
import math
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------
# Chemins et noms de fichiers (noms d'origine du portail de données)
# --------------------------------------------------------------------------
BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"

FICHIERS = {
    "parc": "parc_vehicules.csv",
    "permis": "permis.csv",
    "accidents": "accidents_trafic.csv",
    "etat_routes": "etat_routes.csv",
    "population": "population.csv",
    "routes": "routes_classees.csv",
    "auto_ecoles": "auto_ecoles.csv",
}

TYPES_VEHICULES = {
    "Voitues": "Voitures",  # faute de frappe dans la source
    "Camionnettes": "Camionnettes",
    "Autocars/Autobus": "Autocars et autobus",
    "Camions": "Camions",
    "Semi-remorques": "Semi-remorques",
    "Tracteurs": "Tracteurs",
    "2 roues et assimilées": "Deux-roues et assimilés",
}
GROUPES_VEHICULES = {
    "Voitures": "Voitures et camionnettes",
    "Camionnettes": "Voitures et camionnettes",
    "Deux-roues et assimilés": "Deux-roues",
    "Camions": "Poids lourds",
    "Semi-remorques": "Poids lourds",
    "Autocars et autobus": "Bus et autocars",
    "Tracteurs": "Tracteurs",
}
CATEGORIES_PERMIS = {
    "Moto (A)": ("A", "Moto"),
    "Voiture légèr (B)": ("B", "Voiture légère"),
    "Poids lourd (C)": ("C", "Poids lourd"),
    "Transport en commun (D)": ("D", "Transport en commun"),
    "Semi-remorque (E)": ("E", "Semi-remorque"),
    "Voiture spéciale (F)": ("F", "Voiture spéciale"),
}
INDICATEURS_ACCIDENTS = {
    "Nombre de cas d'accidents de la circulation": "accidents",
    "Nombre de morts": "morts",
    "Nombre de blessés": "blesses",
    "Accidents mortels /100.000 hab": "accidents_pour_100k_hab",
}
TYPES_RESEAU = {
    "ROUTES REVETUES": "Routes revêtues",
    "ROUTES EN TERRES": "Routes en terre",
    "VOIRIES REVETUES": "Voiries revêtues",
    "VOIRIES EN TERRES": "Voiries en terre",
}
ETATS = {"BON": "bon_km", "MOYEN": "moyen_km", "MAUVAIS": "mauvais_km", "TRAVAUX": "travaux_km"}
CODE_REGION = {"K": "Kara", "P": "Plateaux", "C": "Centrale", "S": "Savanes", "M": "Maritime"}
REVETEMENTS_REVETUS = {"Bitume", "Beton", "Pavé"}
REGIONS = ["Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]

# Préfecture présente au recensement mais absente des fichiers routes et auto-écoles.
# Ajoutée pour que la somme des préfectures égale la population de la région (vérifié plus bas).
PREFECTURES_SANS_DONNEES_GEO = {"Mô": "Centrale"}

# Tronçons sans code de région ni nom retrouvé dans les routes classées.
# Attribution faite à la main (connaissance géographique) : À VÉRIFIER / CORRIGER par vous.
REGIONS_MANUELLES = {
    "LOME AKOUMAPE VOGAN ANFOIN (RN4)": "Maritime",
    "DAVIE AMAKPAPE": "Maritime",
    "DAVIE LOME (PASSAGE SUPERIEUR)": "Maritime",
    "RN2/3 AFLAO HILACONDJI FRE BENIN": "Maritime",
    "RN2/3 AFLAO HILACONDJI FRT BENIN RETOUR (CARREFOUR AVEPOZO FRT GHANA)": "Maritime",
    "RN2/3 AFLAO HILACONDJI FRT BENIN RETOUR 2": "Maritime",
    "TSEVIE TABLIGBO ANFOIN ANEHO": "Maritime",
}
REGION_VOIRIES = "Voiries (non régionalisées)"

RAPPORT = []


def log(texte=""):
    print(texte)
    RAPPORT.append(texte)


def titre(texte):
    log("")
    log("=" * 70)
    log(texte)
    log("=" * 70)


# --------------------------------------------------------------------------
# Outils
# --------------------------------------------------------------------------
def cle(nom):
    """Clé de comparaison : sans accents, majuscules, tirets et espaces unifiés."""
    s = unicodedata.normalize("NFKD", str(nom)).encode("ascii", "ignore").decode()
    s = re.sub(r"[-_'’]", " ", s.upper())
    return " ".join(s.split())


def lire(nom):
    return pd.read_csv(RAW / FICHIERS[nom], encoding="utf-8-sig")


def ecrire(df, nom):
    df.to_csv(OUT / nom, index=False, encoding="utf-8-sig")
    log(f"  -> data/processed/{nom} ({len(df)} lignes)")


def longueur_km(wkt):
    """Longueur d'une géométrie MULTILINESTRING (WKT, lon lat) en km (haversine)."""
    total = 0.0
    for partie in re.findall(r"\(([^()]+)\)", wkt):
        pts = [tuple(map(float, p.split())) for p in partie.split(",")]
        for (lon1, lat1), (lon2, lat2) in zip(pts, pts[1:]):
            p1, p2 = math.radians(lat1), math.radians(lat2)
            dp, dl = p2 - p1, math.radians(lon2 - lon1)
            a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
            total += 6371.0088 * 2 * math.asin(math.sqrt(a))
    return total


def verifier_fichiers():
    manquants = [f for f in FICHIERS.values() if not (RAW / f).exists()]
    if manquants:
        print("Fichiers introuvables dans data/raw/ :")
        for f in manquants:
            print("  -", f)
        sys.exit(1)


# --------------------------------------------------------------------------
# 1. Parc de véhicules
# --------------------------------------------------------------------------
def nettoyer_parc():
    titre("1. PARC DE VÉHICULES IMMATRICULÉS (national)")
    df = lire("parc")
    total_source = df[df["types-de-vehicule"] == "Total"].set_index("Date")["Value"]
    d = df[df["types-de-vehicule"] != "Total"].copy()
    d["type_vehicule"] = d["types-de-vehicule"].map(TYPES_VEHICULES)
    inconnus = d.loc[d["type_vehicule"].isna(), "types-de-vehicule"].unique()
    if len(inconnus):
        log(f"  ATTENTION types non reconnus : {list(inconnus)}")
    d["groupe"] = d["type_vehicule"].map(GROUPES_VEHICULES)
    d = d.rename(columns={"Date": "annee", "Value": "valeur"})
    d = d[["annee", "type_vehicule", "groupe", "valeur"]].sort_values(["annee", "type_vehicule"])

    somme = d.groupby("annee")["valeur"].sum()
    ecart = (somme - total_source).dropna()
    mauvais = ecart[ecart != 0]
    log(f"  Années : {d.annee.min()}-{d.annee.max()} ; valeurs manquantes : {int(d.valeur.isna().sum())}")
    log(f"  Unité source : {sorted(df['Unit'].dropna().unique().tolist())} ; valeur = immatriculations annuelles.")
    log("  La ligne « Total » de la source est exclue des types (évite le double comptage).")
    if mauvais.empty:
        log("  Contrôle : la somme des types égale le Total source pour toutes les années.")
    else:
        log(f"  Contrôle : écart avec le Total source pour {len(mauvais)} année(s) : {mauvais.to_dict()}")
    ecrire(d, "parc_vehicules.csv")
    return d


# --------------------------------------------------------------------------
# 2. Permis de conduire
# --------------------------------------------------------------------------
def nettoyer_permis():
    titre("2. PERMIS DE CONDUIRE DÉLIVRÉS (national)")
    df = lire("permis")
    total_source = df[df["categories-de-permis"] == "Total"].set_index("Date")["Value"]
    d = df[df["categories-de-permis"] != "Total"].copy()
    d["categorie"] = d["categories-de-permis"].map(lambda x: CATEGORIES_PERMIS[x][0])
    d["libelle"] = d["categories-de-permis"].map(lambda x: CATEGORIES_PERMIS[x][1])
    d = d.rename(columns={"Date": "annee", "Value": "valeur"})
    d = d[["annee", "categorie", "libelle", "valeur"]]

    annees = range(int(df["Date"].min()), int(df["Date"].max()) + 1)
    categories = sorted(d["categorie"].unique())
    index_complet = pd.MultiIndex.from_product(
        [annees, categories], names=["annee", "categorie"]
    )
    d = d.set_index(["annee", "categorie"]).reindex(index_complet).reset_index()
    libelles = {code: libelle for code, libelle in CATEGORIES_PERMIS.values()}
    d["libelle"] = d["categorie"].map(libelles)
    d = d[["annee", "categorie", "libelle", "valeur"]].sort_values(["annee", "categorie"])

    annees_vides = sorted(
        d.groupby("annee")["valeur"].apply(lambda s: s.isna().all()).loc[lambda s: s].index
    )
    annees_incompletes = {
        int(annee): sorted(set(categories) - set(g.loc[g["valeur"].notna(), "categorie"]))
        for annee, g in d.groupby("annee")
        if g["valeur"].isna().any() and not g["valeur"].isna().all()
    }
    log(f"  Période de la source : {min(annees)}-{max(annees)} ; catégories : {categories}.")
    log(f"  Unité source : {sorted(df['Unit'].dropna().unique().tolist())} ; valeur = permis délivrés durant l'année.")
    if annees_vides:
        log(f"  Années sans aucune valeur par catégorie : {annees_vides} ; les cellules restent vides, pas à zéro.")
    if annees_incompletes:
        log(f"  Catégories manquantes par année : {annees_incompletes}.")
    somme = d.groupby("annee")["valeur"].sum(min_count=1)
    ecart = (somme - total_source.where(total_source != 0)).dropna()
    mauvais = ecart[ecart != 0]
    if mauvais.empty:
        log("  Contrôle : la somme des catégories égale le Total source (hors années vides).")
    else:
        log(f"  Contrôle : écart avec le Total source : {mauvais.to_dict()}")

    moto = d[d.categorie == "A"].set_index("annee")["valeur"]
    pics = moto[moto > 5 * moto.median()]
    if len(pics):
        log(f"  À vérifier : permis moto très supérieurs à la médiane ({moto.median():.0f}) en {pics.to_dict()}")
    ecrire(d, "permis.csv")
    return d, somme


# --------------------------------------------------------------------------
# 3. Accidents (national) et autres indicateurs
# --------------------------------------------------------------------------
def nettoyer_accidents(population_togo_2022):
    titre("3. ACCIDENTS DE LA ROUTE (national)")
    df = lire("accidents")
    coeur = df[df["indicateur"].isin(INDICATEURS_ACCIDENTS)].copy()
    coeur["indicateur"] = coeur["indicateur"].map(INDICATEURS_ACCIDENTS)
    acc = coeur.pivot_table(index="Date", columns="indicateur", values="Value").reset_index()
    acc = acc.rename(columns={
        "Date": "annee",
        "accidents_pour_100k_hab": "taux_accidents_pour_100k_hab_source",
    }).sort_values("annee")
    acc.columns.name = None

    # The historical population cannot be reconstructed independently from the
    # source rate, so population-based rates are published only for the census year.
    acc["population_reference"] = pd.NA
    acc["population_source"] = "Non disponible"
    acc["population_reference"] = acc["population_reference"].astype("Float64")
    acc["morts_pour_100k_hab"] = pd.NA
    acc["blesses_pour_100k_hab"] = pd.NA
    census_year = acc["annee"] == 2022
    acc.loc[census_year, "population_reference"] = population_togo_2022
    acc.loc[census_year, "population_source"] = "Recensement 2022"
    acc.loc[census_year, "morts_pour_100k_hab"] = (
        acc.loc[census_year, "morts"] / population_togo_2022 * 1e5
    )
    acc.loc[census_year, "blesses_pour_100k_hab"] = (
        acc.loc[census_year, "blesses"] / population_togo_2022 * 1e5
    )
    acc["deces_pour_100_accidents"] = acc["morts"] / acc["accidents"] * 100

    taux_2022 = acc.loc[census_year, "taux_accidents_pour_100k_hab_source"].iloc[0]
    verif_2022 = acc.loc[census_year, "accidents"].iloc[0] / population_togo_2022 * 1e5
    log("  Nombres absolus : accidents, blessés et morts conservés séparément (2010-2022).")
    log(f"  Unités source : {coeur['Unit'].dropna().unique().tolist()} ; les trois comptes ne sont pas interchangeables.")
    log("  Population recensée disponible uniquement en 2022 ; les taux morts/blessés par habitant")
    log("  ne sont donc calculés que pour 2022. Aucune population historique n'est déduite du taux source.")
    log(f"  Contrôle 2022 du taux source : accidents/population x 100 000 = {verif_2022:.2f} ; source = {taux_2022:.2f}.")
    log("  Le taux source reste identifié séparément et n'est pas utilisé pour reconstruire la population.")
    log("  Aucun taux par véhicule n'est publié : les données du parc sont des immatriculations annuelles,")
    log("  pas un stock de véhicules en circulation avec un dénominateur compatible.")
    log("  Formules publiées : morts ou blessés / population recensée 2022 x 100 000 (2022 seulement) ;")
    log("  morts / accidents x 100 (ratio brut, pas un taux de mortalité des personnes accidentées).")
    acc = acc.round(2)

    log(f"  Années : {int(acc.annee.min())}-{int(acc.annee.max())} ; accidents au niveau national uniquement.")
    sauts = acc.set_index("annee")["accidents"].pct_change().abs()
    for annee, v in sauts[sauts > 0.5].items():
        log(f"  À vérifier : accidents en variation de {v:.0%} en {int(annee)} (changement de couverture ?).")
    log("  La série véhicules est un flux annuel d'immatriculations ; elle ne constitue pas un stock roulant.")
    ecrire(acc, "accidents_national.csv")

    autres = df[~df["indicateur"].isin(INDICATEURS_ACCIDENTS)].copy()
    autres = autres.rename(columns={"indicateur": "indicateur", "Unit": "unite", "Date": "annee", "Value": "valeur"})
    autres = autres[["indicateur", "unite", "annee", "valeur"]].sort_values(["indicateur", "annee"])
    ecrire(autres, "autres_indicateurs_nationaux.csv")

    # Recoupements avec les autres fichiers
    deux_roues = autres[autres.indicateur.str.contains("deux roues")].set_index("annee")["valeur"]
    log(f"  Recoupement : {len(deux_roues)} années de deux-roues présentes aussi dans ce fichier (ignorées, déjà dans le parc).")
    return acc


# --------------------------------------------------------------------------
# 4. Routes classées et auto-écoles (fichiers géographiques)
# --------------------------------------------------------------------------
def nettoyer_routes():
    titre("4. ROUTES CLASSÉES (tracés)")
    df = lire("routes")
    sans_nom = int(df["route_nom"].isna().sum())
    d = pd.DataFrame({
        "id_route": range(1, len(df) + 1),
        "region": df["region_nom_bdd"],
        "prefecture": df["prefecture_nom_bdd"],
        "commune": df["commune_nom_bdd"],
        "canton": df["canton_nom_bdd"],
        "type_route": df["route_type"],
        "revetement": df["route_recouvrement"],
        "nb_voies": df["voies_nbr"],
        "route_nom": df["route_nom"].fillna("Non renseigné"),
        "longueur_km": df["geometry"].map(longueur_km).round(3),
        "geometry_wkt": df["geometry"],
    })
    d["code_route"] = d["route_nom"].str.extract(r"^(TGR[A-Z0-9]+)")[0]
    d["revetu"] = d["revetement"].isin(REVETEMENTS_REVETUS)
    log(f"  {len(d)} segments, {d.prefecture.nunique()} préfectures, {d.region.nunique()} régions.")
    log(f"  Segments sans nom de route : {sans_nom} (marqués « Non renseigné »).")
    log("  Types de route et revêtements conservés; la colonne route_classee est supprimée (toujours « Oui »).")
    log("  Longueur calculée depuis la géométrie WKT (somme des distances haversine entre sommets, en km).")
    log(f"  Longueur totale : {d.longueur_km.sum():.0f} km dont revêtue : {d.loc[d.revetu, 'longueur_km'].sum():.0f} km.")
    ecrire(d, "routes_classees.csv")
    return d


def nettoyer_auto_ecoles():
    titre("5. AUTO-ÉCOLES")
    df = lire("auto_ecoles")
    coord = df["geometry"].str.extract(r"POINT\s*\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s*\)")
    statut = df["agregation"].replace({"Néant": "Non renseigné"})
    d = pd.DataFrame({
        "id_auto_ecole": range(1, len(df) + 1),
        "region": df["region_nom_bdd"],
        "prefecture": df["prefecture_nom_bdd"],
        "commune": df["commune_nom_bdd"],
        "canton": df["canton_nom_bdd"],
        "localite": df["nom_localite"],
        "nom": df["nom_etablissement"].str.strip(),
        "adresse": df["adresse_etablissement"].replace({"Nsp": pd.NA}),
        "jours_ouverture": df["journee_ouverture"].str.strip("{}").str.replace(",", ", "),
        "statut": statut,
        "longitude": coord[0].astype(float),
        "latitude": coord[1].astype(float),
    })
    d["nb_jours_ouverture"] = d["jours_ouverture"].str.split(", ").str.len()
    d["agreee"] = d["statut"].isin(["Agréée", "Antenne agréée"])
    log(f"  {len(d)} auto-écoles ; sans coordonnées : {int(d.longitude.isna().sum())}.")
    log(f"  Statuts : {d.statut.value_counts().to_dict()}")
    log("  Le fichier source ne contient pas de date d'observation ni d'indicateur d'exhaustivité.")
    log("  Aucune entrée dans une préfecture signifie absence d'enregistrement dans ce fichier, pas absence prouvée de service.")
    log("  Colonne activite_categorie supprimée (toujours « Auto-école »).")
    ecrire(d, "auto_ecoles.csv")
    return d


# --------------------------------------------------------------------------
# 6. Population (recensement 2022) par préfecture et par région
# --------------------------------------------------------------------------
def nettoyer_population(routes, auto_ecoles):
    titre("6. POPULATION 2022")
    df = lire("population")
    df["cle"] = df["découpage-administratif"].map(cle)
    togo = int(df.loc[df["cle"] == "TOGO", "Value"].iloc[0])
    log(f"  Population nationale : {togo:,}".replace(",", " "))

    # Régions du recensement : Lomé (Grand Lomé = DAGL) est séparé de la Maritime
    reg_recens = {n: int(df.loc[df["cle"] == n, "Value"].max()) for n in
                  ["MARITIME", "DAGL", "PLATEAUX", "CENTRALE", "KARA", "SAVANES"]}
    somme = sum(reg_recens.values())
    log(f"  Régions du recensement : {reg_recens}")
    log(f"  Somme des 6 entités = {somme:,} ({'OK' if somme == togo else 'ÉCART avec le national'}).".replace(",", " "))
    log("  Piège réglé : dans le recensement, Lomé (DAGL) est séparé de la Maritime ; dans les fichiers")
    log("  routes et auto-écoles, Golfe et Agoè-Nyivé sont rattachés à la Maritime. La population de la")
    log("  Maritime = Maritime + DAGL pour que les ratios soient comparables.")

    # Préfectures connues des fichiers routes et auto-écoles
    pref = pd.concat([routes[["region", "prefecture"]], auto_ecoles[["region", "prefecture"]]]).drop_duplicates()
    doublons = pref[pref.duplicated("prefecture", keep=False)]
    if len(doublons):
        log(f"  ATTENTION préfecture dans plusieurs régions : {doublons.to_dict('records')}")
    pref = pref.drop_duplicates("prefecture")
    connues = {cle(x) for x in pref["prefecture"]}
    extra = [{"region": r, "prefecture": n} for n, r in PREFECTURES_SANS_DONNEES_GEO.items() if cle(n) not in connues]
    if extra:
        pref = pd.concat([pref, pd.DataFrame(extra)])
        log(f"  Préfecture(s) ajoutée(s) car absente(s) des fichiers routes et auto-écoles : {[e['prefecture'] for e in extra]}.")
    pref = pref.sort_values(["region", "prefecture"]).reset_index(drop=True)

    pops, methodes = [], []
    for nom in pref["prefecture"]:
        k = cle(nom)
        lignes = df[df["cle"] == k]
        if len(lignes):
            # une même appellation peut désigner préfecture, commune et canton : la préfecture est la plus grande
            pops.append(int(lignes["Value"].max()))
            methodes.append("ligne préfecture")
        else:
            communes = df[df["cle"].str.match(rf"^{re.escape(k)} \d+$")]
            pops.append(int(communes["Value"].sum()) if len(communes) else pd.NA)
            methodes.append(f"somme de {len(communes)} communes" if len(communes) else "introuvable")
    pref["population_2022"] = pops
    pref["methode"] = methodes
    for _, r in pref[pref.methode != "ligne préfecture"].iterrows():
        log(f"  Préfecture {r.prefecture} : {r.methode}.")

    controle = pref.groupby("region")["population_2022"].sum()
    attendu = {"Maritime": reg_recens["MARITIME"] + reg_recens["DAGL"], "Plateaux": reg_recens["PLATEAUX"],
               "Centrale": reg_recens["CENTRALE"], "Kara": reg_recens["KARA"], "Savanes": reg_recens["SAVANES"]}
    log("  Contrôle somme des préfectures par région / population de la région :")
    for r in REGIONS:
        s, a = int(controle.get(r, 0)), attendu[r]
        log(f"    {r:9s} {s:>10,} / {a:>10,}  ({'OK' if s == a else f'écart {s - a:+,}'})".replace(",", " "))

    ecrire(pref, "population_prefectures.csv")
    pop_regions = pd.DataFrame({"region": REGIONS, "population_2022": [attendu[r] for r in REGIONS]})
    log("  Communes : non utilisées (numérotation différente d'un fichier à l'autre : « Amou 3 »,")
    log("  « Binah 2 », « Danyi 1+Danyi 2 »...). Le niveau préfecture est fiable ; le filtre")
    log("  « Commune » du tableau de bord est donc à retirer ou à limiter.")
    return pref, pop_regions, togo


# --------------------------------------------------------------------------
# 7. État des routes (2020)
# --------------------------------------------------------------------------
def nettoyer_etat_routes(routes):
    titre("7. ÉTAT DU RÉSEAU ROUTIER (2020)")
    df = lire("etat_routes")
    df = df.rename(columns={"tronçon": "troncon"})
    df["type_reseau"] = df["indicateur"].map(TYPES_RESEAU)
    df["est_total"] = df["troncon"].str.strip().str.upper().str.startswith("TOTAL")

    # Les lignes « TOTAL » et « TOTAL RT » servent uniquement de contrôle
    totaux_source = (df[df.est_total & (df.etat != "TOTAL")]
                     .pivot_table(index="type_reseau", columns="etat", values="Value", aggfunc="sum"))
    d = df[~df.est_total & (df.etat != "TOTAL")].copy()
    d["etat_col"] = d["etat"].map(ETATS)
    large = (d.pivot_table(index=["type_reseau", "troncon"], columns="etat_col", values="Value", aggfunc="sum")
               .reindex(columns=list(ETATS.values())).reset_index())
    large.columns.name = None
    large["travaux_enregistrement_source_present"] = large["travaux_km"].notna()
    for col in ETATS.values():
        large[col] = large[col].fillna(0.0)
    large["total_km"] = large[list(ETATS.values())].sum(axis=1)

    # Région d'un tronçon : voirie -> à part ; lettre du code (TGRK = Kara...) ; attribution manuelle ;
    # sinon recherche du nom dans les routes classées (région où se trouve le plus de km).
    km_nom = routes.assign(k=routes["route_nom"].map(cle)).groupby(["k", "region"])["longueur_km"].sum()
    noms_routes = sorted({k for k, _ in km_nom.index})
    regions, sources, traversees = [], [], []
    for _, ligne in large.iterrows():
        nom = ligne["troncon"]
        k = cle(nom)
        m = re.match(r"^TGR([A-Z])", nom.upper())
        if ligne["type_reseau"].startswith("Voiries"):
            reg, src, trav = REGION_VOIRIES, "voirie", ""
        elif m and m.group(1) in CODE_REGION:
            reg, src, trav = CODE_REGION[m.group(1)], "code du tronçon", CODE_REGION[m.group(1)]
        elif k in REGIONS_MANUELLES:
            reg, src, trav = REGIONS_MANUELLES[k], "manuel (à vérifier)", REGIONS_MANUELLES[k]
        else:
            hits = [rn for rn in noms_routes if len(k) > 6 and (k in rn or rn in k)]
            if hits:
                par_region = km_nom.loc[hits].groupby(level="region").sum().sort_values(ascending=False)
                reg, src, trav = par_region.index[0], "nom de route", ", ".join(sorted(par_region.index))
            else:
                reg, src, trav = "Non attribué", "aucune", ""
        regions.append(reg); sources.append(src); traversees.append(trav)
    large["region"] = regions
    large["source_region"] = sources
    large["regions_traversees"] = traversees
    large["annee"] = 2020
    large = large[["annee", "type_reseau", "troncon", "region", "source_region", "regions_traversees",
                   "travaux_enregistrement_source_present"] + list(ETATS.values()) + ["total_km"]].round(2)

    log(f"  {len(large)} tronçons ({large.type_reseau.value_counts().to_dict()}).")
    log("  Lignes « TOTAL » et « TOTAL RT » de la source retirées des tronçons (sinon doubles comptages) ;")
    travaux_absents = int((~large["travaux_enregistrement_source_present"]).sum())
    log("  État « TRAVAUX » traité séparément; une ligne source absente est encodée à 0 km mais reste signalée.")
    log(f"  Enregistrement TRAVAUX absent pour {travaux_absents} tronçon(s) : 0 signifie aucune valeur listée, pas une mesure explicite.")
    log("  Un seul millésime (2020) : pas d'évolution possible, seulement une photo par région.")
    log("  Contrôle : somme des tronçons contre les totaux de la source :")
    somme = large.groupby("type_reseau")[list(ETATS.values())].sum()
    for t in totaux_source.index:
        src = totaux_source.loc[t]
        mine = somme.loc[t]
        ecarts = {e: round(float(mine[ETATS[e]] - src[e]), 2) for e in ETATS
                  if e in src.index and pd.notna(src[e]) and abs(mine[ETATS[e]] - src[e]) > 0.05}
        log(f"    {t:18s} {'OK' if not ecarts else 'écarts ' + str(ecarts)}")
    routes_seules = large[large.type_reseau.isin(["Routes revêtues", "Routes en terre"])]
    attribue = routes_seules[routes_seules.region != "Non attribué"]
    log(f"  Part des routes (km) rattachée à une région : {attribue.total_km.sum() / routes_seules.total_km.sum():.1%}")
    log(f"    dont attribution manuelle à vérifier : {routes_seules[routes_seules.source_region.str.startswith('manuel')].total_km.sum():.0f} km")
    multi = routes_seules[routes_seules.regions_traversees.str.contains(",")]
    log(f"    tronçons traversant plusieurs régions (km affectés à la région dominante) : {len(multi)}")
    na = routes_seules[routes_seules.region == "Non attribué"]
    for t in na["troncon"]:
        log(f"    non attribué : {t}")
    ecrire(large, "etat_routes.csv")
    return large


# --------------------------------------------------------------------------
# 8. Tableaux prêts pour le tableau de bord
# --------------------------------------------------------------------------
def construire_indicateurs(routes, auto_ecoles, pref, pop_regions, etat):
    titre("8. INDICATEURS PAR PRÉFECTURE ET PAR RÉGION")
    # préfectures
    ae = auto_ecoles.groupby("prefecture").agg(auto_ecoles=("id_auto_ecole", "count"), auto_ecoles_agreees=("agreee", "sum"))
    rt = routes.groupby("prefecture").agg(routes_km=("longueur_km", "sum"))
    rt["routes_revetues_km"] = routes[routes.revetu].groupby("prefecture")["longueur_km"].sum()
    p = pref.drop(columns="methode").set_index("prefecture").join(ae).join(rt).fillna({"auto_ecoles": 0, "auto_ecoles_agreees": 0})
    p["auto_ecoles_entree_presente"] = p.index.isin(ae.index)
    p["routes_entree_presente"] = p.index.isin(rt.index)
    p["routes_revetues_km"] = p["routes_revetues_km"].where(p["routes_km"].notna(), pd.NA).fillna(0.0).where(p["routes_km"].notna())
    p["auto_ecoles"] = p["auto_ecoles"].astype(int)
    p["auto_ecoles_agreees"] = p["auto_ecoles_agreees"].astype(int)
    p["auto_ecoles_pour_100k_hab"] = (
        p["auto_ecoles"] / p["population_2022"] * 1e5
    ).where(p["auto_ecoles_entree_presente"]).round(2)
    p["routes_km_pour_1000_hab"] = (p["routes_km"] / p["population_2022"] * 1000).round(3)
    p = p.round({"routes_km": 1, "routes_revetues_km": 1}).reset_index()
    ecrire(p, "indicateurs_prefectures.csv")
    log("  Les indicateurs préfectoraux distinguent maintenant entrée présente et aucune ligne source.")
    log("  Les ratios d'auto-écoles/préfecture restent descriptifs : inventaire sans millésime / population du recensement 2022.")

    # régions
    r = pop_regions.set_index("region")
    r["nb_prefectures"] = p.groupby("region")["prefecture"].count()
    r["auto_ecoles"] = p.groupby("region")["auto_ecoles"].sum()
    r["auto_ecoles_agreees"] = p.groupby("region")["auto_ecoles_agreees"].sum()
    r["auto_ecoles_pour_100k_hab"] = (r["auto_ecoles"] / r["population_2022"] * 1e5).round(2)
    r["routes_km"] = routes.groupby("region")["longueur_km"].sum().round(1)
    r["routes_km_pour_1000_hab"] = (r["routes_km"] / r["population_2022"] * 1000).round(3)
    etat_reg = (etat[etat.type_reseau.isin(["Routes revêtues", "Routes en terre"])]
                .groupby("region")[list(ETATS.values()) + ["total_km"]].sum().round(1))
    etat_reg = etat_reg.add_prefix("etat_")
    r = r.join(etat_reg)
    for col in ETATS.values():
        r[f"part_{col.replace('_km', '')}_pct"] = (r[f"etat_{col}"] / r["etat_total_km"] * 100).round(1)
    r = r.reset_index()
    ecrire(r, "indicateurs_regions.csv")
    log("  Formules territoriales préparées : auto-écoles listées / population 2022 x 100 000 ;")
    log("  longueur de routes classées / population 2022 x 1 000 ; part d'état = km d'un état / total km d'état x 100.")
    log("  Le ratio de routes par population n'est pas une densité par superficie; aucune superficie n'est fournie.")
    log("  Comparaison véhicules/permis dans l'interface : valeur annuelle / première valeur commune de la période x 100.")
    log("  Un indice base 100 compare les variations, pas les volumes; il ne démontre pas de lien causal.")
    log("  Rappel : l'état des routes ne concerne que les routes (revêtues et en terre) rattachées à une")
    log("  région ; les tronçons « Non attribué » sont exclus de ces parts.")
    log("  Provenance : les fichiers bruts ne contiennent pas d'URL source ni de date d'extraction par jeu.")
    return p, r


def main():
    verifier_fichiers()
    OUT.mkdir(parents=True, exist_ok=True)
    log("NETTOYAGE DES DONNÉES - Mobilité et sécurité routière au Togo")
    nettoyer_parc()
    nettoyer_permis()
    routes = nettoyer_routes()
    auto_ecoles = nettoyer_auto_ecoles()
    pref, pop_regions, togo = nettoyer_population(routes, auto_ecoles)
    nettoyer_accidents(togo)
    etat = nettoyer_etat_routes(routes)
    construire_indicateurs(routes, auto_ecoles, pref, pop_regions, etat)
    (OUT / "rapport_qualite.txt").write_text("\n".join(RAPPORT), encoding="utf-8")
    print("\nTerminé. Rapport complet : data/processed/rapport_qualite.txt")


if __name__ == "__main__":
    main()
 